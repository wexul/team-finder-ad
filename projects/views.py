from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.http import require_POST

from team_finder.constants import (
    HTTP_ERROR_STATUS,
    HTTP_OK_STATUS,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    SKILL_SUGGEST_LIMIT,
)
from team_finder.pagination import paginate_queryset
from team_finder.validators import normalize_spaces

from .forms import ProjectForm
from .models import Project, Skill


FORBIDDEN_MESSAGE = "Действие доступно только автору проекта"
PROJECT_CLOSED_MESSAGE = "Проект закрыт"
OWNER_PARTICIPANT_MESSAGE = "Автор уже является участником проекта"
EMPTY_NAME_MESSAGE = "Название навыка не может быть пустым"
SKILL_REQUIRED_MESSAGE = "Передайте skill_id или название навыка"
SKILL_NOT_IN_PROJECT_MESSAGE = "Навык не добавлен к проекту"


def project_list(request):
    active_skill = request.GET.get("skill", "").strip()
    projects = Project.objects.select_related("owner").prefetch_related("skills")

    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = paginate_queryset(request, projects.distinct())
    context = {
        "projects": page_obj.object_list,
        "page_obj": page_obj,
        "all_skills": Skill.objects.all(),
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants",
            "skills",
        ),
        pk=project_id,
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method != "POST" or not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    messages.success(request, "Проект опубликован")
    return redirect("projects:detail", project_id=project.pk)


@login_required
@require_http_methods(["GET", "POST"])
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return HttpResponseForbidden(
            "Редактировать проект может только автор"
        )

    form = ProjectForm(request.POST or None, instance=project)

    if request.method != "POST" or not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True, "project": project},
        )

    form.save()
    messages.success(request, "Проект обновлён")
    return redirect("projects:detail", project_id=project.pk)


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": HTTP_ERROR_STATUS, "message": FORBIDDEN_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save(update_fields=["status"])

    return JsonResponse(
        {"status": HTTP_OK_STATUS, "project_status": project.status}
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner == request.user:
        return JsonResponse(
            {
                "status": HTTP_ERROR_STATUS,
                "message": OWNER_PARTICIPANT_MESSAGE,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    if not project.is_open:
        return JsonResponse(
            {"status": HTTP_ERROR_STATUS, "message": PROJECT_CLOSED_MESSAGE},
            status=HTTPStatus.BAD_REQUEST,
        )

    is_participating = project.participants.filter(
        pk=request.user.pk
    ).exists()
    if is_participating:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse(
        {"status": HTTP_OK_STATUS, "participating": not is_participating}
    )


@require_GET
def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()

    if query:
        skills = skills.filter(name__istartswith=query)

    data = list(skills.values("id", "name")[:SKILL_SUGGEST_LIMIT])
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": HTTP_ERROR_STATUS, "message": FORBIDDEN_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

    skill_id = request.POST.get("skill_id")
    raw_name = request.POST.get("name")
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif raw_name:
        name = normalize_spaces(raw_name)
        if not name:
            return JsonResponse(
                {"status": HTTP_ERROR_STATUS, "message": EMPTY_NAME_MESSAGE},
                status=HTTPStatus.BAD_REQUEST,
            )
        try:
            with transaction.atomic():
                skill, created = Skill.objects.get_or_create(
                    name__iexact=name,
                    defaults={"name": name},
                )
        except IntegrityError:
            skill = Skill.objects.get(name__iexact=name)
    else:
        return JsonResponse(
            {"status": HTTP_ERROR_STATUS, "message": SKILL_REQUIRED_MESSAGE},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_was_added = project.skills.filter(pk=skill.pk).exists()
    project.skills.add(skill)
    return JsonResponse(
        {
            "skill_id": skill.pk,
            "name": skill.name,
            "created": created,
            "added": not skill_was_added,
        }
    )


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": HTTP_ERROR_STATUS, "message": FORBIDDEN_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {
                "status": HTTP_ERROR_STATUS,
                "message": SKILL_NOT_IN_PROJECT_MESSAGE,
            },
            status=HTTPStatus.NOT_FOUND,
        )

    project.skills.remove(skill)
    return JsonResponse(
        {"status": HTTP_OK_STATUS, "removed": True, "skill_id": skill.pk}
    )
