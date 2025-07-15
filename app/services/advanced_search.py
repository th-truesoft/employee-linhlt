from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, case, desc, asc
from fuzzywuzzy import fuzz
import re

from app.models.employee import Employee, Department, Position, Location
from app.schemas.employee import (
    EmployeeSearchFilters,
    EmployeeSearchResult,
    SearchSuggestion,
)


class AdvancedSearchService:
    """Service for advanced employee search with full-text search, fuzzy matching, and relevance scoring"""

    def __init__(self):
        pass

    def search_employees(
        self, db: Session, filters: EmployeeSearchFilters, organization_id: str
    ) -> Tuple[List[EmployeeSearchResult], int, Dict[str, Any]]:
        """
        Advanced search for employees with relevance scoring

        Returns: (results, total_count, search_metadata)
        """

        # Start with base query
        query = db.query(Employee).filter(Employee.organization_id == organization_id)
        count_query = db.query(func.count(Employee.id)).filter(
            Employee.organization_id == organization_id
        )

        # Join related tables for search
        query = query.outerjoin(Department).outerjoin(Position).outerjoin(Location)
        count_query = (
            count_query.outerjoin(Department).outerjoin(Position).outerjoin(Location)
        )

        search_metadata = {
            "search_term": filters.search_term,
            "fuzzy_match": filters.fuzzy_match,
            "exact_match": filters.exact_match,
            "fields_searched": filters.search_fields or ["name", "email"],
            "filters_applied": [],
            "sorting": {"sort_by": filters.sort_by, "sort_order": filters.sort_order},
        }

        # Apply basic filters
        if filters.status:
            query = query.filter(Employee.status.in_(filters.status))
            count_query = count_query.filter(Employee.status.in_(filters.status))
            search_metadata["filters_applied"].append(f"status: {filters.status}")

        if filters.department_ids:
            query = query.filter(Employee.department_id.in_(filters.department_ids))
            count_query = count_query.filter(
                Employee.department_id.in_(filters.department_ids)
            )
            search_metadata["filters_applied"].append(
                f"departments: {filters.department_ids}"
            )

        if filters.position_ids:
            query = query.filter(Employee.position_id.in_(filters.position_ids))
            count_query = count_query.filter(
                Employee.position_id.in_(filters.position_ids)
            )
            search_metadata["filters_applied"].append(
                f"positions: {filters.position_ids}"
            )

        if filters.location_ids:
            query = query.filter(Employee.location_id.in_(filters.location_ids))
            count_query = count_query.filter(
                Employee.location_id.in_(filters.location_ids)
            )
            search_metadata["filters_applied"].append(
                f"locations: {filters.location_ids}"
            )

        # Advanced filters
        if filters.email_domain:
            query = query.filter(Employee.email.like(f"%@{filters.email_domain}"))
            count_query = count_query.filter(
                Employee.email.like(f"%@{filters.email_domain}")
            )
            search_metadata["filters_applied"].append(
                f"email_domain: {filters.email_domain}"
            )

        if filters.phone_prefix:
            query = query.filter(Employee.phone.like(f"{filters.phone_prefix}%"))
            count_query = count_query.filter(
                Employee.phone.like(f"{filters.phone_prefix}%")
            )
            search_metadata["filters_applied"].append(
                f"phone_prefix: {filters.phone_prefix}"
            )

        if filters.has_email is not None:
            if filters.has_email:
                query = query.filter(Employee.email.isnot(None), Employee.email != "")
                count_query = count_query.filter(
                    Employee.email.isnot(None), Employee.email != ""
                )
            else:
                query = query.filter(
                    or_(Employee.email.is_(None), Employee.email == "")
                )
                count_query = count_query.filter(
                    or_(Employee.email.is_(None), Employee.email == "")
                )
            search_metadata["filters_applied"].append(f"has_email: {filters.has_email}")

        if filters.has_phone is not None:
            if filters.has_phone:
                query = query.filter(Employee.phone.isnot(None), Employee.phone != "")
                count_query = count_query.filter(
                    Employee.phone.isnot(None), Employee.phone != ""
                )
            else:
                query = query.filter(
                    or_(Employee.phone.is_(None), Employee.phone == "")
                )
                count_query = count_query.filter(
                    or_(Employee.phone.is_(None), Employee.phone == "")
                )
            search_metadata["filters_applied"].append(f"has_phone: {filters.has_phone}")

        # Date range filters
        if filters.created_after:
            query = query.filter(Employee.created_at >= filters.created_after)
            count_query = count_query.filter(
                Employee.created_at >= filters.created_after
            )
            search_metadata["filters_applied"].append(
                f"created_after: {filters.created_after}"
            )

        if filters.created_before:
            query = query.filter(Employee.created_at <= filters.created_before)
            count_query = count_query.filter(
                Employee.created_at <= filters.created_before
            )
            search_metadata["filters_applied"].append(
                f"created_before: {filters.created_before}"
            )

        if filters.updated_after:
            query = query.filter(Employee.updated_at >= filters.updated_after)
            count_query = count_query.filter(
                Employee.updated_at >= filters.updated_after
            )
            search_metadata["filters_applied"].append(
                f"updated_after: {filters.updated_after}"
            )

        if filters.updated_before:
            query = query.filter(Employee.updated_at <= filters.updated_before)
            count_query = count_query.filter(
                Employee.updated_at <= filters.updated_before
            )
            search_metadata["filters_applied"].append(
                f"updated_before: {filters.updated_before}"
            )

        # Apply search term with relevance scoring
        relevance_score = None
        if filters.search_term:
            search_term = filters.search_term.strip()
            search_fields = filters.search_fields or ["name", "email"]

            if filters.exact_match:
                # Exact match search
                search_conditions = []
                for field in search_fields:
                    if field == "name":
                        if filters.case_sensitive:
                            search_conditions.append(Employee.name == search_term)
                        else:
                            search_conditions.append(
                                func.lower(Employee.name) == search_term.lower()
                            )
                    elif field == "email":
                        if filters.case_sensitive:
                            search_conditions.append(Employee.email == search_term)
                        else:
                            search_conditions.append(
                                func.lower(Employee.email) == search_term.lower()
                            )
                    elif field == "department" and Department.name:
                        if filters.case_sensitive:
                            search_conditions.append(Department.name == search_term)
                        else:
                            search_conditions.append(
                                func.lower(Department.name) == search_term.lower()
                            )
                    elif field == "position" and Position.name:
                        if filters.case_sensitive:
                            search_conditions.append(Position.name == search_term)
                        else:
                            search_conditions.append(
                                func.lower(Position.name) == search_term.lower()
                            )
                    elif field == "location" and Location.name:
                        if filters.case_sensitive:
                            search_conditions.append(Location.name == search_term)
                        else:
                            search_conditions.append(
                                func.lower(Location.name) == search_term.lower()
                            )

                if search_conditions:
                    search_filter = or_(*search_conditions)
                    query = query.filter(search_filter)
                    count_query = count_query.filter(search_filter)

            else:
                # Full-text search with relevance scoring
                if not filters.case_sensitive:
                    search_term = search_term.lower()

                # Create relevance score calculation
                relevance_cases = []
                search_conditions = []

                for field in search_fields:
                    if field == "name":
                        field_column = (
                            func.lower(Employee.name)
                            if not filters.case_sensitive
                            else Employee.name
                        )
                        # Exact match gets highest score
                        relevance_cases.append(
                            case((field_column == search_term, 1.0), else_=0)
                        )
                        # Starts with gets medium-high score
                        relevance_cases.append(
                            case((field_column.like(f"{search_term}%"), 0.8), else_=0)
                        )
                        # Contains gets medium score
                        relevance_cases.append(
                            case((field_column.like(f"%{search_term}%"), 0.6), else_=0)
                        )
                        # Add to search conditions
                        search_conditions.append(field_column.like(f"%{search_term}%"))

                    elif field == "email":
                        field_column = (
                            func.lower(Employee.email)
                            if not filters.case_sensitive
                            else Employee.email
                        )
                        relevance_cases.append(
                            case((field_column == search_term, 1.0), else_=0)
                        )
                        relevance_cases.append(
                            case((field_column.like(f"{search_term}%"), 0.7), else_=0)
                        )
                        relevance_cases.append(
                            case((field_column.like(f"%{search_term}%"), 0.5), else_=0)
                        )
                        search_conditions.append(field_column.like(f"%{search_term}%"))

                    elif field == "department":
                        field_column = (
                            func.lower(Department.name)
                            if not filters.case_sensitive
                            else Department.name
                        )
                        relevance_cases.append(
                            case((field_column == search_term, 0.9), else_=0)
                        )
                        relevance_cases.append(
                            case((field_column.like(f"%{search_term}%"), 0.4), else_=0)
                        )
                        search_conditions.append(field_column.like(f"%{search_term}%"))

                    elif field == "position":
                        field_column = (
                            func.lower(Position.name)
                            if not filters.case_sensitive
                            else Position.name
                        )
                        relevance_cases.append(
                            case((field_column == search_term, 0.9), else_=0)
                        )
                        relevance_cases.append(
                            case((field_column.like(f"%{search_term}%"), 0.4), else_=0)
                        )
                        search_conditions.append(field_column.like(f"%{search_term}%"))

                    elif field == "location":
                        field_column = (
                            func.lower(Location.name)
                            if not filters.case_sensitive
                            else Location.name
                        )
                        relevance_cases.append(
                            case((field_column == search_term, 0.8), else_=0)
                        )
                        relevance_cases.append(
                            case((field_column.like(f"%{search_term}%"), 0.3), else_=0)
                        )
                        search_conditions.append(field_column.like(f"%{search_term}%"))

                if search_conditions:
                    search_filter = or_(*search_conditions)
                    query = query.filter(search_filter)
                    count_query = count_query.filter(search_filter)

                    # Calculate total relevance score
                    if relevance_cases and filters.include_relevance_score:
                        # Sum all relevance scores and normalize
                        total_relevance = sum(relevance_cases)
                        # Cap at 1.0 maximum
                        relevance_score = case(
                            (total_relevance > 1.0, 1.0), else_=total_relevance
                        )
                        query = query.add_columns(
                            relevance_score.label("relevance_score")
                        )

            search_metadata["search_applied"] = True
            search_metadata["search_term_processed"] = search_term

        # Apply sorting
        if filters.sort_by:
            sort_column = None
            if filters.sort_by == "name":
                sort_column = Employee.name
            elif filters.sort_by == "email":
                sort_column = Employee.email
            elif filters.sort_by == "created_at":
                sort_column = Employee.created_at
            elif filters.sort_by == "updated_at":
                sort_column = Employee.updated_at
            elif filters.sort_by == "department":
                sort_column = Department.name
            elif filters.sort_by == "position":
                sort_column = Position.name
            elif filters.sort_by == "location":
                sort_column = Location.name
            elif filters.sort_by == "relevance" and relevance_score is not None:
                sort_column = relevance_score

            if sort_column is not None:
                if filters.sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        elif relevance_score is not None:
            # Default sort by relevance if searching
            query = query.order_by(desc(relevance_score))
        else:
            # Default sort by name
            query = query.order_by(Employee.name)

        # Get total count before pagination
        total_count = count_query.scalar()

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute query
        if relevance_score is not None and filters.include_relevance_score:
            # Query returns tuples (Employee, relevance_score)
            results = query.all()
            employees = []
            for result in results:
                if isinstance(result, tuple):
                    employee, score = result
                    employees.append((employee, float(score) if score else 0.0))
                else:
                    employees.append((result, 0.0))
        else:
            # Query returns Employee objects
            employees = [(emp, None) for emp in query.all()]

        # Convert to search results
        search_results = []
        for employee, score in employees:
            # Apply fuzzy matching for name if enabled
            fuzzy_score = None
            if (
                filters.fuzzy_match
                and filters.search_term
                and filters.search_term.strip()
            ):
                fuzzy_score = (
                    fuzz.ratio(filters.search_term.lower(), employee.name.lower())
                    / 100.0
                )
                # Use fuzzy score if better than relevance score or if no relevance score
                if score is None or fuzzy_score > score:
                    score = fuzzy_score

            result = EmployeeSearchResult(
                id=employee.id,
                name=employee.name,
                email=employee.email,
                phone=employee.phone,
                status=employee.status,
                department=employee.department.name if employee.department else None,
                position=employee.position.name if employee.position else None,
                location=employee.location.name if employee.location else None,
                created_at=employee.created_at,
                updated_at=employee.updated_at,
                relevance_score=score if filters.include_relevance_score else None,
            )
            search_results.append(result)

        search_metadata["total_results"] = total_count
        search_metadata["page_results"] = len(search_results)

        return search_results, total_count, search_metadata

    def get_search_suggestions(
        self, db: Session, search_term: str, organization_id: str, limit: int = 10
    ) -> List[SearchSuggestion]:
        """
        Get search suggestions based on partial search term
        """

        suggestions = []
        search_term = search_term.lower().strip()

        if not search_term:
            return suggestions

        # Name suggestions
        name_results = (
            db.query(Employee.name, func.count(Employee.id))
            .filter(
                Employee.organization_id == organization_id,
                func.lower(Employee.name).like(f"%{search_term}%"),
            )
            .group_by(Employee.name)
            .order_by(func.count(Employee.id).desc())
            .limit(limit)
            .all()
        )

        for name, count in name_results:
            suggestions.append(
                SearchSuggestion(suggestion=name, type="name", count=count)
            )

        # Department suggestions
        dept_results = (
            db.query(Department.name, func.count(Employee.id))
            .join(Employee)
            .filter(
                Employee.organization_id == organization_id,
                func.lower(Department.name).like(f"%{search_term}%"),
            )
            .group_by(Department.name)
            .order_by(func.count(Employee.id).desc())
            .limit(limit)
            .all()
        )

        for dept_name, count in dept_results:
            suggestions.append(
                SearchSuggestion(suggestion=dept_name, type="department", count=count)
            )

        # Position suggestions
        pos_results = (
            db.query(Position.name, func.count(Employee.id))
            .join(Employee)
            .filter(
                Employee.organization_id == organization_id,
                func.lower(Position.name).like(f"%{search_term}%"),
            )
            .group_by(Position.name)
            .order_by(func.count(Employee.id).desc())
            .limit(limit)
            .all()
        )

        for pos_name, count in pos_results:
            suggestions.append(
                SearchSuggestion(suggestion=pos_name, type="position", count=count)
            )

        # Location suggestions
        loc_results = (
            db.query(Location.name, func.count(Employee.id))
            .join(Employee)
            .filter(
                Employee.organization_id == organization_id,
                func.lower(Location.name).like(f"%{search_term}%"),
            )
            .group_by(Location.name)
            .order_by(func.count(Employee.id).desc())
            .limit(limit)
            .all()
        )

        for loc_name, count in loc_results:
            suggestions.append(
                SearchSuggestion(suggestion=loc_name, type="location", count=count)
            )

        # Sort by relevance (fuzzy match score) and count
        def suggestion_score(suggestion):
            fuzzy_score = fuzz.ratio(search_term, suggestion.suggestion.lower()) / 100.0
            # Combine fuzzy score with count (normalized)
            count_score = min(suggestion.count / 100.0, 1.0)  # Normalize count
            return (fuzzy_score * 0.7) + (count_score * 0.3)

        suggestions.sort(key=suggestion_score, reverse=True)

        return suggestions[:limit]
