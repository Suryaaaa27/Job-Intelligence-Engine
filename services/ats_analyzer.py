"""
ATS Analyzer
============

Generates an ATS compatibility report using the MatchResult
produced by the ResumeMatcher.

This module DOES NOT recalculate resume matching.
Instead it evaluates ATS readiness and resume quality.
"""

from __future__ import annotations

import re
from collections import Counter

from schemas.resume_schema import (
    ATSReport,
    MatchResult,
    StructuredJD,
    StructuredResume,
)

# ==========================================================
# Constants
# ==========================================================

ACTION_VERBS = {
    "achieved",
    "analyzed",
    "architected",
    "automated",
    "built",
    "collaborated",
    "created",
    "deployed",
    "designed",
    "developed",
    "engineered",
    "evaluated",
    "implemented",
    "improved",
    "integrated",
    "led",
    "managed",
    "migrated",
    "optimized",
    "performed",
    "planned",
    "reduced",
    "resolved",
    "trained",
}

FILLER_WORDS = {
    "very",
    "really",
    "quite",
    "various",
    "many",
    "multiple",
    "different",
    "several",
}

NUMBER_PATTERN = re.compile(
    r"\d+|\d+\.\d+|%|\+|million|billion|thousand",
    re.IGNORECASE,
)

WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]*")


class ATSAnalyzer:
    """
    ATS compatibility analyzer.
    """

    # ==========================================================
    # Text Helpers
    # ==========================================================

    @staticmethod
    def _resume_text(
        resume: StructuredResume,
    ) -> str:

        chunks = []

        if resume.summary:
            chunks.append(resume.summary)

        chunks.extend(resume.skills)
        chunks.extend(resume.tools_technologies)

        chunks.extend(resume.projects)

        chunks.extend(resume.education)

        chunks.extend(resume.certifications)

        for exp in resume.experience:
            chunks.extend(exp.bullets)

        return "\n".join(chunks).lower()


    @staticmethod
    def _words(
        text: str,
    ) -> list[str]:

        return WORD_PATTERN.findall(text.lower())


    # ==========================================================
    # Keyword Analysis
    # ==========================================================

    @staticmethod
    def _missing_keywords(
        resume: StructuredResume,
        jd: StructuredJD,
    ) -> list[str]:

        text = ATSAnalyzer._resume_text(resume)

        missing = []

        keywords = (
            jd.responsibilities
            + jd.qualifications
        )

        for keyword in keywords:

            if keyword.lower() not in text:
                missing.append(keyword)

        return sorted(set(missing))


    @staticmethod
    def _keyword_density(
        resume: StructuredResume,
        jd: StructuredJD,
    ) -> float:

        text = ATSAnalyzer._resume_text(resume)

        keywords = (
            jd.required_skills
            + jd.preferred_skills
            + jd.tools_technologies
        )

        if not keywords:
            return 100.0

        matched = 0

        for keyword in keywords:

            if keyword.lower() in text:
                matched += 1

        return round(
            matched / len(keywords) * 100,
            1,
        )


    # ==========================================================
    # Action Verb Analysis
    # ==========================================================

    @staticmethod
    def _action_verb_score(
        resume: StructuredResume,
    ) -> float:

        bullets = []

        for exp in resume.experience:
            bullets.extend(exp.bullets)

        if not bullets:
            return 0

        score = 0

        for bullet in bullets:

            words = bullet.lower().split()

            if words and words[0] in ACTION_VERBS:
                score += 1

        return round(
            score / len(bullets) * 100,
            1,
        )


    # ==========================================================
    # Impact Analysis
    # ==========================================================

    @staticmethod
    def _impact_score(
        resume: StructuredResume,
    ) -> float:

        bullets = []

        for exp in resume.experience:
            bullets.extend(exp.bullets)

        if not bullets:
            return 0

        quantified = 0

        for bullet in bullets:

            if NUMBER_PATTERN.search(bullet):
                quantified += 1

        return round(
            quantified / len(bullets) * 100,
            1,
        )


    # ==========================================================
    # Readability
    # ==========================================================

    @staticmethod
    def _readability_score(
        resume: StructuredResume,
    ) -> float:

        text = ATSAnalyzer._resume_text(resume)

        words = ATSAnalyzer._words(text)

        if not words:
            return 0

        avg_word_length = sum(
            len(word)
            for word in words
        ) / len(words)

        filler_count = sum(
            1
            for word in words
            if word in FILLER_WORDS
        )

        score = 100

        if avg_word_length > 8:
            score -= 10

        score -= filler_count

        return max(
            0,
            round(score, 1),
        )


    # ==========================================================
    # Formatting
    # ==========================================================

    @staticmethod
    def _formatting_issues(
        resume: StructuredResume,
    ) -> list[str]:

        issues = []

        contact = resume.contact_info or {}

        if not contact.get("email"):
            issues.append("Missing email")

        if not contact.get("phone"):
            issues.append("Missing phone")

        if not resume.summary:
            issues.append(
                "Missing professional summary"
            )

        for exp in resume.experience:

            if len(exp.bullets) < 2:
                issues.append(
                    f"{exp.title}: Too few bullet points"
                )

            for bullet in exp.bullets:

                if len(bullet) > 180:
                    issues.append(
                        "Very long experience bullet"
                    )

        for project in resume.projects:

            if len(project) > 250:
                issues.append(
                    "Very long project description"
                )


        return sorted(set(issues))


    # ==========================================================
    # Weak Section Analysis
    # ==========================================================

    @staticmethod
    def _weak_sections(
        resume: StructuredResume,
    ) -> list[str]:

        weak = []

        # Summary
        if not resume.summary or len(resume.summary.strip()) < 35:
            weak.append("summary")

        # Experience
        if not resume.experience:
            weak.append("experience")
        else:

            total_bullets = sum(
                len(exp.bullets)
                for exp in resume.experience
            )

            if total_bullets < 4:
                weak.append("experience")

        # Projects
        if not resume.projects:
            weak.append("projects")

        # Education
        if not resume.education:
            weak.append("education")

        return weak


    # ==========================================================
    # Project Analysis
    # ==========================================================

    @staticmethod
    def _project_score(
        resume: StructuredResume,
        jd: StructuredJD,
    ) -> float:

        if not resume.projects:
            return 0.0

        project_text = " ".join(
            resume.projects
        ).lower()

        keywords = (
            jd.required_skills
            + jd.preferred_skills
            + jd.tools_technologies
        )

        if not keywords:
            return 100.0

        matched = 0

        for keyword in keywords:

            if keyword.lower() in project_text:
                matched += 1

        coverage = matched / len(keywords)

        score = 50 + coverage * 50

        return round(
            min(score, 100),
            1,
        )


    # ==========================================================
    # Resume Strength Detection
    # ==========================================================

    @staticmethod
    def _strengths(
        resume: StructuredResume,
        match_result: MatchResult,
    ) -> list[str]:

        strengths = []

        if match_result.skills_score >= 80:
            strengths.append(
                "Strong technical skill alignment"
            )

        if match_result.experience_score >= 80:
            strengths.append(
                "Relevant professional experience"
            )

        if len(resume.projects) >= 3:
            strengths.append(
                "Strong project portfolio"
            )

        if len(resume.experience) >= 2:
            strengths.append(
                "Multiple professional experiences"
            )

        if resume.total_experience_years:

            if resume.total_experience_years >= 2:
                strengths.append(
                    "Good industry exposure"
                )

        if len(resume.certifications) >= 2:
            strengths.append(
                "Multiple certifications"
            )

        if len(resume.skills) >= 15:
            strengths.append(
                "Broad technical skillset"
            )

        return strengths


    # ==========================================================
    # Resume Recommendations
    # ==========================================================

    @staticmethod
    def _recommendations(
        resume: StructuredResume,
        jd: StructuredJD,
        match_result: MatchResult,
        formatting_issues: list[str],
        weak_sections: list[str],
    ) -> list[str]:

        recommendations = []

        # Missing required skills

        for skill in match_result.missing_required_skills:

            recommendations.append(
                f"Add or highlight experience with '{skill}'."
            )

        # Missing preferred skills

        for skill in match_result.missing_preferred_skills:

            recommendations.append(
                f"Consider mentioning '{skill}' if applicable."
            )

        # Summary

        if "summary" in weak_sections:

            recommendations.append(
                "Write a concise professional summary tailored to the target role."
            )

        # Projects

        if "projects" in weak_sections:

            recommendations.append(
                "Include 2–4 technical projects with measurable impact."
            )

        # Experience

        if "experience" in weak_sections:

            recommendations.append(
                "Expand experience bullets with achievements instead of responsibilities."
            )

        # Formatting

        recommendations.extend(formatting_issues)

        return sorted(set(recommendations))


    # ==========================================================
    # Overall ATS Score
    # ==========================================================

    @staticmethod
    def _overall_score(
        match_result: MatchResult,
        project_score: float,
        action_score: float,
        impact_score: float,
        keyword_density: float,
        readability_score: float,
        formatting_issues: list[str],
        weak_sections: list[str],
    ) -> float:

        score = (

            match_result.match_score * 0.50

            + project_score * 0.10

            + action_score * 0.10

            + impact_score * 0.10

            + keyword_density * 0.10

            + readability_score * 0.10

        )

        # Small penalties

        score -= len(formatting_issues) * 1.5

        score -= len(weak_sections) * 2

        score = max(
            0,
            min(score, 100),
        )

        return round(score, 1)


    # ==========================================================
    # Public API
    # ==========================================================

    def analyze(
        self,
        resume: StructuredResume,
        jd: StructuredJD,
        match_result: MatchResult,
    ) -> ATSReport:
        """
        Generates an ATSReport using the existing MatchResult
        without recomputing resume matching.
        """

        # ------------------------------------------------------
        # Derived Scores
        # ------------------------------------------------------

        project_score = self._project_score(
            resume,
            jd,
        )

        action_score = self._action_verb_score(
            resume,
        )

        impact_score = self._impact_score(
            resume,
        )

        keyword_density = self._keyword_density(
            resume,
            jd,
        )

        readability_score = self._readability_score(
            resume,
        )

        formatting_issues = self._formatting_issues(
            resume,
        )

        weak_sections = self._weak_sections(
            resume,
        )

        strengths = self._strengths(
            resume,
            match_result,
        )

        recommendations = self._recommendations(
            resume,
            jd,
            match_result,
            formatting_issues,
            weak_sections,
        )

        overall_score = self._overall_score(
            match_result=match_result,
            project_score=project_score,
            action_score=action_score,
            impact_score=impact_score,
            keyword_density=keyword_density,
            readability_score=readability_score,
            formatting_issues=formatting_issues,
            weak_sections=weak_sections,
        )

        # ------------------------------------------------------
        # Report
        # ------------------------------------------------------

        return ATSReport(

            overall_score=overall_score,

            skills_score=match_result.skills_score,
            experience_score=match_result.experience_score,
            education_score=match_result.education_score,
            certification_score=match_result.certification_score,

            project_score=project_score,

            action_verb_score=action_score,
            impact_score=impact_score,
            keyword_density_score=keyword_density,
            formatting_score=max(
                0,
                100 - len(formatting_issues) * 10,
            ),
            readability_score=readability_score,

            missing_skills=sorted(
                set(
                    match_result.missing_required_skills
                    + match_result.missing_preferred_skills
                )
            ),

            missing_keywords=self._missing_keywords(
                resume,
                jd,
            ),

            weak_sections=weak_sections,

            formatting_issues=formatting_issues,

            strengths=strengths,

            recommendations=recommendations,
        )