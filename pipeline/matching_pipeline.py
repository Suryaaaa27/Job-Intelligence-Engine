from services.resume_matcher import ResumeMatcher


class MatchingPipeline:

    @staticmethod
    def execute(resume, jd):

        return ResumeMatcher.match(
            resume,
            jd,
        )