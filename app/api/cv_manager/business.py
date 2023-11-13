import datetime
import logging
import os
from tempfile import TemporaryDirectory

from fastapi import UploadFile, HTTPException, Response

from app.core.models.PG_pandasmodels import COLLAB_PG
from app.core.shared_modules.stringhandler import StringHandler
from app.models.collabs import PG_Collabs
from app.models.cvs import PG_CVs
from app.schema.cv_manager import CVUploadRequest, CVDownloadRequest, CVDownloadResponse
from app.core import azure_blob_manager, azure_pg_manager
from fastapi.responses import FileResponse


class CVManagerBusiness:

    @staticmethod
    def etl_business(request: CVUploadRequest, file: UploadFile):
        cv_names = {}
        with TemporaryDirectory() as temp_dir:
            new_name = f"{CVManagerBusiness.get_time_stamp()} {file.filename}"
            hash_name = StringHandler.generate_unique_id(
                StringHandler.normalize_string(
                    f"{request.f_name}{request.l_name}",
                    remove_special_chars=True))
            if CVManagerBusiness.check_collab_exist(hash_name):
                cv_names[new_name] = hash_name
                binary_data = file.file.read()
                azure_blob_manager.upload_file(new_name, binary_data)
                if type(binary_data) == bytes:
                    with open(os.path.join(temp_dir, new_name), "wb") as writer:
                        writer.write(binary_data)
                logging.info(
                    f"Collab {request.f_name} {request.l_name} is uploaded")
                CVManagerBusiness.start_ETL(temp_dir, cv_names)
            else:
                raise HTTPException(status_code=412, detail="Collaborateur introuvable")

        return {
            "JSON Payload ": request.dict(),
            "Filenames": [file.filename for file in [file]],
        }

    @staticmethod
    def download_cv(request : CVDownloadRequest)->Response:
        file_name = PG_CVs().get_cv_name_by_id(request.cv_id)
        if not file_name:
            raise HTTPException(status_code=400, detail="CV Introuvable")
        file_name=file_name[0] # get cv_name. the format is ($cv_name)
        if request.type == "file":
            file = azure_blob_manager.download_file(file_name)
            return Response(status_code=200, content=file, media_type='application/octet-stream')
        elif request.type == "link":
            return Response(status_code=200, content=str(dict(CVDownloadResponse(link=azure_blob_manager.get_file_url(file_name)))))

    @staticmethod
    def get_time_stamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    @staticmethod
    def check_collab_exist(collab_id: str) -> bool:
        return azure_pg_manager.check_existance(PG_Collabs.__tablename__, COLLAB_PG.collab_id, collab_id)

    @staticmethod
    def start_ETL(data_path, collab_ids):
        from app.settings import Settings
        settings = Settings()
        # =============================================================================
        # # extract text
        # =============================================================================
        from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
        extractor = FileMassExtractor()
        # get text dataframe. One row per documents
        df_text = extractor.read_all_documents(data_path, collab_ids, read_only_extensions=[], ignore_extensions=[])
        if df_text is None:
            return
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
        embedder = ChunkEmbedder(settings=settings)
        df_embeddings = embedder.embed_chunk_dataframe(df_chunks)
        # =============================================================================
        # # parse the chunks
        # =============================================================================
        from app.core.cv_information_retrieval.LLMparser import LLMParser
        parser = LLMParser(settings=settings)
        parsed_chunks = parser.parse_all_chunks(df_chunks)
        # =============================================================================
        # # consolidate CVs
        # =============================================================================
        from app.core.cv_information_retrieval.CVstructurator import CvStructurator
        cv_structurator = CvStructurator()
        df_struct_cvs = cv_structurator.consolidate_cvs(parsed_chunks)
        # =============================================================================
        # # consolidate profiles
        # =============================================================================
        from app.core.cv_information_retrieval.profilestructurator import ProfileStructurator
        structurator = ProfileStructurator()
        df_profiles = structurator.consolidate_profiles(df_struct_cvs)
        # =============================================================================
        # # make pg tables
        # =============================================================================
        from app.core.cv_information_retrieval.tablemaker import TableMaker
        maker = TableMaker()
        pg_profiles, pg_chunks, pg_cvs = maker.make_pg_tables(
            df_profiles,
            df_embeddings)
        # =============================================================================
        # # save to pg
        # =============================================================================
        from app.core.azure_modules.azurePGmanager import AzurePGManager
        azure_pg_manager.save(
            pg_profiles=pg_profiles,
            pg_chunks=pg_chunks,
            pg_cvs=pg_cvs,
        )
