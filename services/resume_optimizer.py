"""
Resume Optimizer
================

Generates actionable resume improvement suggestions
based on:

- Structured Resume
- Structured JD
- MatchResult
- ATSReport

This module DOES NOT modify the resume.
It only produces optimization recommendations.
"""

from __future__ import annotations

from schemas.resume_schema import (
    ATSReport,
    MatchResult,
    ResumeOptimization,
    StructuredJD,
    StructuredResume,
)


class ResumeOptimizer:
    """
    Generates resume improvement recommendations.
    """

    # ==========================================================
    # Summary Suggestions
    # ==========================================================

    @staticmethod
    def _summary_suggestions(
        resume: StructuredResume,
        jd: StructuredJD,
    ) -> list[str]:

        suggestions = []

        summary = (resume.summary or "").lower()

        if not summary:

            suggestions.append(
                "Add a professional summary tailored to the target role."
            )

            return suggestions

        important_keywords = (
            jd.required_skills
            + jd.preferred_skills
        )

        missing = []

        for keyword in important_keywords:

            if keyword.lower() not in summary:
                missing.append(keyword)

        if missing:

            suggestions.append(
                "Include important keywords in the summary such as: "
                + ", ".join(sorted(set(missing[:5])))
            )

        if len(summary.split()) < 30:

            suggestions.append(
                "Expand the professional summary to better highlight technical expertise and career achievements."
            )

        return suggestions

    # ==========================================================
    # Skill Suggestions
    # ==========================================================

    @staticmethod
    def _skill_suggestions(
        match_result: MatchResult,
    ) -> list[str]:

        suggestions = []

        for skill in match_result.missing_required_skills:

            suggestions.append(
                f"Add '{skill}' if you possess this skill."
            )

        for skill in match_result.missing_preferred_skills:

            suggestions.append(
                f"Consider mentioning '{skill}' where relevant."
            )

        if not suggestions:

            suggestions.append(
                "Technical skills are well aligned with the Job Description."
            )

        return suggestions

    # ==========================================================
    # Experience Suggestions
    # ==========================================================

    @staticmethod
    def _experience_suggestions(
        resume: StructuredResume,
        ats_report: ATSReport,
    ) -> list[str]:

        suggestions = []

        if not resume.experience:

            suggestions.append(
                "Add professional experience or internships."
            )

            return suggestions

        if ats_report.action_verb_score < 70:

            suggestions.append(
                "Begin experience bullets with strong action verbs such as Designed, Developed, Built, Implemented, Optimized or Led."
            )

        if ats_report.impact_score < 70:

            suggestions.append(
                "Quantify achievements using percentages, revenue, time savings, user counts or measurable business impact."
            )

        total_bullets = sum(
            len(exp.bullets)
            for exp in resume.experience
        )

        if total_bullets < 5:

            suggestions.append(
                "Provide more achievement-oriented bullet points for each experience."
            )

        long_bullets = 0

        for exp in resume.experience:

            for bullet in exp.bullets:

                if len(bullet) > 180:
                    long_bullets += 1

        if long_bullets:

            suggestions.append(
                "Reduce lengthy experience bullets to improve readability."
            )

        if not suggestions:

            suggestions.append(
                "Experience section is well optimized."
            )

        return suggestions
    
        # ==========================================================
    # Project Suggestions
    # ==========================================================

    @staticmethod
    def _project_suggestions(
        resume: StructuredResume,
        jd: StructuredJD,
        ats_report: ATSReport,
    ) -> list[str]:

        suggestions = []

        if not resume.projects:

            suggestions.append(
                "Add 2–4 technical projects relevant to the target role."
            )

            return suggestions

        project_text = " ".join(
            resume.projects
        ).lower()

        missing_keywords = []

        keywords = (
            jd.required_skills
            + jd.preferred_skills
            + jd.tools_technologies
        )

        for keyword in keywords:

            if keyword.lower() not in project_text:
                missing_keywords.append(keyword)

        if missing_keywords:

            suggestions.append(
                "Highlight project experience with technologies such as: "
                + ", ".join(sorted(set(missing_keywords[:6])))
            )

        if ats_report.impact_score < 70:

            suggestions.append(
                "Include measurable project outcomes such as accuracy improvements, latency reduction, revenue impact, or user growth."
            )

        for project in resume.projects:

            if len(project.split()) < 20:

                suggestions.append(
                    "Expand project descriptions to explain problem, solution, technologies and results."
                )

                break

        if not suggestions:

            suggestions.append(
                "Projects are well aligned with the Job Description."
            )

        return suggestions


    # ==========================================================
    # Education Suggestions
    # ==========================================================

    @staticmethod
    def _education_suggestions(
        resume: StructuredResume,
        match_result: MatchResult,
    ) -> list[str]:

        suggestions = []

        if not resume.education:

            suggestions.append(
                "Add your educational qualifications."
            )

            return suggestions

        if match_result.missing_education:

            suggestions.append(
                "Mention education that satisfies the Job Description requirements."
            )

        if not suggestions:

            suggestions.append(
                "Education section adequately matches the target role."
            )

        return suggestions


    # ==========================================================
    # Certification Suggestions
    # ==========================================================

    @staticmethod
    def _certification_suggestions(
        resume: StructuredResume,
        match_result: MatchResult,
    ) -> list[str]:

        suggestions = []

        if match_result.missing_certifications:

            for cert in match_result.missing_certifications:

                suggestions.append(
                    f"Consider obtaining or highlighting '{cert}'."
                )

        elif not resume.certifications:

            suggestions.append(
                "Add relevant certifications to strengthen your profile."
            )

        else:

            suggestions.append(
                "Certification section is satisfactory."
            )

        return suggestions


    # ==========================================================
    # Formatting Suggestions
    # ==========================================================

    @staticmethod
    def _formatting_suggestions(
        ats_report: ATSReport,
    ) -> list[str]:

        suggestions = []

        if ats_report.formatting_issues:

            suggestions.extend(
                ats_report.formatting_issues
            )

        if ats_report.readability_score < 70:

            suggestions.append(
                "Improve readability by shortening lengthy sentences and avoiding filler words."
            )

        if ats_report.formatting_score < 80:

            suggestions.append(
                "Use consistent headings, spacing and bullet formatting throughout the resume."
            )

        if not suggestions:

            suggestions.append(
                "Formatting is ATS-friendly."
            )

        return sorted(set(suggestions))


    # ==========================================================
    # Priority Actions
    # ==========================================================

    @staticmethod
    def _priority_actions(
        ats_report: ATSReport,
        match_result: MatchResult,
    ) -> list[str]:

        actions = []

        # Highest priority
        for skill in match_result.missing_required_skills:

            actions.append(
                f"Add or demonstrate experience with '{skill}'."
            )

        # Medium priority

        if ats_report.action_verb_score < 70:

            actions.append(
                "Rewrite experience bullets using strong action verbs."
            )

        if ats_report.impact_score < 70:

            actions.append(
                "Add quantified achievements throughout the resume."
            )

        if ats_report.keyword_density_score < 70:

            actions.append(
                "Increase Job Description keyword coverage naturally across the resume."
            )

        if "summary" in ats_report.weak_sections:

            actions.append(
                "Rewrite the professional summary for the target role."
            )

        if "projects" in ats_report.weak_sections:

            actions.append(
                "Strengthen project descriptions with technical depth and measurable impact."
            )

        if ats_report.formatting_score < 80:

            actions.append(
                "Fix ATS formatting issues."
            )

        return actions
    
        # ==========================================================
    # Public API
    # ==========================================================

    def optimize(
        self,
        resume: StructuredResume,
        jd: StructuredJD,
        match_result: MatchResult,
        ats_report: ATSReport,
    ) -> ResumeOptimization:
        """
        Generate resume optimization recommendations.

        This method consumes:
            - Structured Resume
            - Structured Job Description
            - MatchResult
            - ATSReport

        It never recalculates resume matching.
        """

        summary = self._summary_suggestions(
            resume,
            jd,
        )

        experience = self._experience_suggestions(
            resume,
            ats_report,
        )

        projects = self._project_suggestions(
            resume,
            jd,
            ats_report,
        )

        skills = self._skill_suggestions(
            match_result,
        )

        education = self._education_suggestions(
            resume,
            match_result,
        )

        certifications = self._certification_suggestions(
            resume,
            match_result,
        )

        formatting = self._formatting_suggestions(
            ats_report,
        )

        priority_actions = self._priority_actions(
            ats_report,
            match_result,
        )

        # Remove duplicates while preserving order
        summary = list(dict.fromkeys(summary))
        experience = list(dict.fromkeys(experience))
        projects = list(dict.fromkeys(projects))
        skills = list(dict.fromkeys(skills))
        education = list(dict.fromkeys(education))
        certifications = list(dict.fromkeys(certifications))
        formatting = list(dict.fromkeys(formatting))
        priority_actions = list(dict.fromkeys(priority_actions))

        return ResumeOptimization(

            summary=summary,

            experience=experience,

            projects=projects,

            skills=skills,

            education=education,

            certifications=certifications,

            formatting=formatting,

            priority_actions=priority_actions,
        )