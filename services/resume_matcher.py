"""
Resume Matcher Service
======================

Coordinates all resume-job matching modules and produces
a MatchResult.
"""

from matching.corpus import build_resume_corpus
from matching.skills import match_skills
from matching.experience import match_experience
from matching.education import match_education
from matching.certification import match_certifications
from matching.keywords import match_keywords
from matching.scoring import (
    MatchScores,
    calculate_overall_score,
)

from schemas.resume_schema import (
    StructuredResume,
    StructuredJD,
    MatchResult,
)


class ResumeMatcher:
    """Compares a parsed resume with a structured job description."""

    @staticmethod
    def match(
        resume: StructuredResume,
        jd: StructuredJD,
    ) -> MatchResult:
        """
        Compare a structured resume with a structured job description.
        """

        # ---------------------------------------
        # Build searchable resume corpus
        # ---------------------------------------

        corpus = build_resume_corpus(resume)

        # ---------------------------------------
        # Skills
        # ---------------------------------------

        skill_result = match_skills(
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills,
            corpus=corpus,
        )

        # ---------------------------------------
        # Experience
        # ---------------------------------------

        experience_result = match_experience(
            candidate_years=resume.total_experience_years,
            required_years=jd.min_experience_years,
        )

        # ---------------------------------------
        # Education
        # ---------------------------------------

        education_result = match_education(
            required_education=jd.education_requirements,
            corpus=corpus,
        )

        # ---------------------------------------
        # Certifications
        # ---------------------------------------

        certification_result = match_certifications(
            required_certifications=jd.certifications,
            corpus=corpus,
        )

        # ---------------------------------------
        # Keywords
        # ---------------------------------------

        keyword_result = match_keywords(
            responsibilities=jd.responsibilities,
            qualifications=jd.qualifications,
            corpus=corpus,
        )

        # ---------------------------------------
        # Temporary lexical score
        #
        # (Replace later with semantic matching)
        # ---------------------------------------

        lexical_score = keyword_result.keyword_score

        # ---------------------------------------
        # Overall score
        # ---------------------------------------

        overall_score = calculate_overall_score(
            MatchScores(
                skills=skill_result.skills_score,
                experience=experience_result.experience_score,
                education=education_result.education_score,
                certification=certification_result.certification_score,
                keyword=keyword_result.keyword_score,
                lexical=lexical_score,
            )
        )

        # ---------------------------------------
        # Final Result
        # ---------------------------------------

        return MatchResult(
            match_score=overall_score,

            matched_required_skills=skill_result.matched_required,
            matched_preferred_skills=skill_result.matched_preferred,

            missing_required_skills=skill_result.missing_required,
            missing_preferred_skills=skill_result.missing_preferred,

            missing_education=education_result.missing_education,
            missing_certifications=certification_result.missing_certifications,

            experience_gap_years=experience_result.experience_gap_years,

            skills_score=round(skill_result.skills_score * 100, 2),
            experience_score=round(experience_result.experience_score * 100, 2),
            education_score=round(education_result.education_score * 100, 2),
            certification_score=round(
                certification_result.certification_score * 100,
                2,
            ),
            keyword_score=round(keyword_result.keyword_score * 100, 2),
            semantic_score=round(lexical_score * 100, 2),

            skill_gaps=skill_result.skill_gaps,
        )