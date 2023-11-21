"""Created on Tue Aug  8 15:47:38 2023

@author: agarc

"""
import logging

from app.core.cv_information_retrieval.docx_reader import DOCXReader
from app.core.cv_information_retrieval.pdf_reader import PDFReader
from app.core.cv_information_retrieval.pptx_reader import PPTXReader
from app.core.cv_information_retrieval.txt_reader import TXTReader
from app.core.models.etl_pandasmodels import TextDF
from app.core.shared_modules.pathexplorer import PathExplorer
from app.core.shared_modules.stringhandler import StringHandler


# =============================================================================
# FileReader (inherits from PathExplorer)
# =============================================================================
class FileReader:
    """Extract text from a single document.
    Readers are in specific classes (one class per extension, add to self.loader_router
    and imports)
    """

    def __init__(self) -> None:
        # list of valid extensions for which a loader is ready.
        # TODO add functions to read .doc, .ppt
        self.loader_router = {
            ".pptx": PPTXReader.read_text,
            ".docx": DOCXReader.read_text,
            ".pdf": PDFReader.read_text,
            ".txt": TXTReader.read_text,
        }

    # =============================================================================
    # user functions
    # =============================================================================
    def read_single_document(self, file_path: str) -> dict | None:
        """Read a single documents.
        Uses the execution to send to the appropriate text extractor

        :param file_path: file path
        :return: hashmap with file information and text
        """
        if PathExplorer.assert_file_exists(file_path) is False:
            return None
        file_extension = PathExplorer.get_single_file_extension(file_path)
        file_name = PathExplorer.get_single_file_name(file_path)

        # if the extension is valid:
        if file_extension in self.loader_router:
            # extract the text
            text = self.loader_router[file_extension](file_path)
            # clean the text
            text = self._clean_text(text)
            # dump into a hashmap
            if text:
                """cv_id is generated
                StringHandler.generate_unique_id
                (StringHandler.normalize_string(meta_cv))"""
                meta_cv = file_extension + file_name + text
                cv_id = StringHandler.generate_unique_id(
                    StringHandler.normalize_string(meta_cv),
                )
                text_and_metadata = {
                    TextDF.file_path: file_path,
                    TextDF.file_name: file_name,
                    TextDF.file_extension: file_extension,
                    TextDF.file_full_name: file_name + file_extension,
                    TextDF.file_text: text,
                    TextDF.cv_id: cv_id,
                }
                return text_and_metadata
            else:
                logging.warning(
                    f"No text detected in file: {file_name}{file_extension}",
                )
                return None
        # else pass
        else:
            logging.warning(f"Not readable format:{file_extension}")
            return None

    # =============================================================================
    # internal functions
    # =============================================================================
    def _clean_text(self, text: str) -> str:
        cleaned_text = text
        return cleaned_text


if __name__ == "__main__":
    reader = FileReader()
    file_path = r"data_dev/data_1_1cv/Talan - CV - Mehdi IKBAL - 202108 - Paris.pptx"
    content = reader.read_single_document(file_path)
    print(content)
