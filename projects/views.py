from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProjectForm
from .models import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN, Project, Skill

PER_PAGE = 12
SKILL_SUGGEST_LIMIT = 10


def project_list(request):
    active_skill = request.GET.get("skill") or ""
    projects = Project.objects.select_related("owner").prefetch_related("skills").order_by("-created_at")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects.distinct(), PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "all_skills": Skill.objects.order_by("name"),
            "active_skill": active_skill,
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
@require_http_methods(["GET", "POST"])
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, "Проект опубликован")
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
@require_http_methods(["GET", "POST"])
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Редактировать проект может только автор")

    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Проект обновлён")
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True, "project": project})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "forbidden"}, status=403)
    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner == request.user:
        return JsonResponse({"status": "error", "message": "owner_already_participant"}, status=400)
    if not project.is_open:
        return JsonResponse({"status": "error", "message": "project_closed"}, status=400)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participating = False
    else:
        project.participants.add(request.user)
        participating = True
    return JsonResponse({"status": "ok", "participating": participating})


@require_GET
def skills_autocomplete(request):
    query = (request.GET.get("q") or "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__istartswith=query)
    data = list(skills.order_by("name").values("id", "name")[:SKILL_SUGGEST_LIMIT])
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "forbidden"}, status=403)

    skill_id = request.POST.get("skill_id")
    raw_name = request.POST.get("name")
    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif raw_name:
        name = " ".join(raw_name.strip().split())
        if not name:
            return JsonResponse({"status": "error", "message": "empty_name"}, status=400)
        try:
            with transaction.atomic():
                skill, created = Skill.objects.get_or_create(name__iexact=name, defaults={"name": name})
        except IntegrityError:
            skill = Skill.objects.get(name__iexact=name)
            created = False
    else:
        return JsonResponse({"status": "error", "message": "skill_id_or_name_required"}, status=400)

    before = project.skills.filter(pk=skill.pk).exists()
    project.skills.add(skill)
    return JsonResponse({"skill_id": skill.pk, "name": skill.name, "created": created, "added": not before})


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error", "message": "forbidden"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "error", "message": "skill_not_in_project"}, status=404)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok", "removed": True, "skill_id": skill.pk})
