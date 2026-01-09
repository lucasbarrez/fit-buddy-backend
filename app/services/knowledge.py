import os
import glob
from typing import List

ASSETS_DIR = "assets/Documentation pour développement/Exemples_markdowns_sport"

class KnowledgeService:
    @staticmethod
    def _read_markdown_files(directory: str) -> str:
        """Reads all markdown files in a subdirectory and returns combined text."""
        path = os.path.join(os.getcwd(), ASSETS_DIR, directory, "*.md")
        combined_text = ""
        for file_path in glob.glob(path):
            with open(file_path, "r", encoding="utf-8") as f:
                combined_text += f"\n\n--- Source: {os.path.basename(file_path)} ---\n"
                combined_text += f.read()
        return combined_text

    def get_construction_guidelines(self) -> str:
        """Returns guidelines from 'contruction-de-programme' and 'principe-de-base'."""
        text = self._read_markdown_files("principe-de-base")
        text += self._read_markdown_files("contruction-de-programme")
        return text

    def get_muscle_group_info(self, muscle_groups: List[str]) -> str:
        """
        Returns info for specific exercises/muscle groups.
        Naive implementation: reads all files in 'exercices' and lets LLM filter/use relevance.
        Optimized: could match filenames to muscle groups.
        """
        # For prototype simplicity, we read all exercise guidance as "Expert Reference"
        return self._read_markdown_files("exercices")
                
    def get_profile_adaptation(self, profile_type: str) -> str:
        # e.g. read "adaptation-au-profil"
        return self._read_markdown_files("adaptation-au-profil")
