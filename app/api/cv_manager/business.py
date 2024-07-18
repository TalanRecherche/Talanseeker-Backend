import datetime
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException, Response, UploadFile

from app.core.azure_modules import azure_blob_manager, azure_pg_manager
from app.core.shared_modules.stringhandler import StringHandler
from app.exceptions.exceptions import CvExceptionError
from app.models.collabs import PgCollabs
from app.models.cvs import PgCvs
from app.schema.cv_manager import CVDownloadRequest, CVDownloadResponse, CVUploadRequest


class CVManagerBusiness:
    @staticmethod
    def etl_business(request: CVUploadRequest, file: UploadFile) -> dict:
        cv_names = {}
        with TemporaryDirectory() as temp_dir:
            new_name = f"{CVManagerBusiness.get_time_stamp()} {file.filename}"
            mail = request.mail
            # Before checking the user, verify the mail
            if request.mail is not None and CVManagerBusiness.check_collab_exist_email(mail):
                hash_name = azure_pg_manager.get_collabs_associated_email(
                    PgCollabs.__tablename__,
                    mail,
                )
            else:
                hash_name = StringHandler.generate_unique_id(
                    StringHandler.normalize_string(
                    f"{request.f_name}{request.l_name}",
                        remove_special_chars=True,
                    ),
            )
            # Check if the collab exist
            if CVManagerBusiness.check_collab_exist(hash_name):
                cv_names[new_name] = hash_name
                binary_data = file.file.read()
                azure_blob_manager.upload_file(new_name, binary_data)
                if isinstance(binary_data, bytes):
                    with Path(Path(temp_dir) / new_name).open("wb") as writer:
                        writer.write(binary_data)
                log_string = f"Collab {request.f_name} {request.l_name} is uploaded"
                logging.info(log_string)
                CVManagerBusiness.start_etl(temp_dir, cv_names)
            else:
                logging.warning("Collab doesn't exist")
                raise HTTPException(status_code=412, detail="Collaborateur introuvable")

        return {
            "JSON Payload ": request.dict(),
            "Filenames": [file.filename for file in [file]],
        }

    @staticmethod
    def download_cv(request: CVDownloadRequest) -> Response | None:
        file_name = PgCvs().get_cv_name_by_id(request.cv_id)
        if not file_name:
            raise HTTPException(status_code=400, detail="CV Introuvable")
        file_name = file_name[0]  # get cv_name. the format is ($cv_name)
        if request.type == "file":
            file = azure_blob_manager.download_file(file_name)
            return Response(
                status_code=200,
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}"},
                content=file,
                media_type="application/octet-stream",
            )
        if request.type == "link":
            return Response(
                status_code=200,
                content=str(
                    dict(
                        CVDownloadResponse(
                            link=azure_blob_manager.get_file_url(file_name),
                        ),
                    ),
                ),
            )
        return None

    @staticmethod
    def get_time_stamp() -> str:
        return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H_%M_%S")

    @staticmethod
    def check_collab_exist(collab_id: str) -> bool:
        return azure_pg_manager.check_existence(
            PgCollabs.__tablename__,
            collab_id,
        )

    @staticmethod
    def check_collab_exist_email(email_id: str) -> bool:
        return azure_pg_manager.check_existence_email(
            PgCollabs.__tablename__,
            email_id,
        )

    @staticmethod
    def start_etl(data_path: str, collab_ids: dict) -> None:

        # =============================================================================
        # # extract text
        # =============================================================================
        from app.core.cv_information_retrieval.filemassextractor import (
            FileMassExtractor,
        )

        extractor = FileMassExtractor()
        # get text dataframe. One row per documents
        df_text = extractor.read_all_documents(
            data_path,
            collab_ids,
            read_only_extensions=[],
            ignore_extensions=[],
        )
        if df_text is None:
            raise CvExceptionError
        # =============================================================================
        # # make the chunks
        # =============================================================================
        from app.core.cv_information_retrieval.chunker import Chunker

        chunker = Chunker()
        # make chunks, One row per chunks
        df_chunks = chunker.chunk_documents(df_text)
        # =============================================================================
        # # compute embeddings
        # =============================================================================
        from app.core.cv_information_retrieval.chunkembedder import ChunkEmbedder

        embedder = ChunkEmbedder()
        df_embeddings = embedder.embed_chunk_dataframe(df_chunks)
        # =============================================================================
        # # parse the chunks
        # =============================================================================
        from app.core.cv_information_retrieval.llm_parser import LLMParser

        parser = LLMParser()
        parsed_chunks = parser.parse_all_chunks(df_chunks)
        # =============================================================================
        # # consolidate CVs
        # =============================================================================
        from app.core.cv_information_retrieval.cv_structurator import CvStructurator

        cv_structurator = CvStructurator()
        df_struct_cvs = cv_structurator.consolidate_cvs(parsed_chunks)
        # =============================================================================
        # # consolidate profiles
        # =============================================================================
        from app.core.cv_information_retrieval.profilestructurator import (
            ProfileStructurator,
        )

        structurator = ProfileStructurator()
        df_profiles = structurator.consolidate_profiles(df_struct_cvs)
        # =============================================================================
        # # make pg tables
        # =============================================================================
        from app.core.cv_information_retrieval.tablemaker import TableMaker

        maker = TableMaker()
        pg_profiles, pg_chunks, pg_cvs = maker.make_pg_tables(
            df_profiles,
            df_embeddings,
        )
        # =============================================================================
        # # save to pg
        # =============================================================================

        azure_pg_manager.save(
            pg_profiles=pg_profiles,
            pg_chunks=pg_chunks,
            pg_cvs=pg_cvs,
        )
