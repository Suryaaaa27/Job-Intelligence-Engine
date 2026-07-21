from services.resume_service import ResumeService


class ResumePipeline:

    @staticmethod
    def execute(file_path: str):

        structured_resume = ResumeService.parse(file_path)

        return structured_resume