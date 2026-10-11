import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from issues.models import Reporter, Issue, CriticalIssue, LowPriorityIssue

REPORTERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reporters.json')
ISSUES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'issues.json')


def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


@csrf_exempt
def reporters(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reporter = Reporter(
            id=data['id'],
            name=data.get('name', ''),
            email=data.get('email', ''),
            team=data.get('team', '')
        )
        try:
            reporter.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        all_reporters = load_json(REPORTERS_FILE)
        all_reporters.append(reporter.to_dict())
        save_json(REPORTERS_FILE, all_reporters)
        return JsonResponse(reporter.to_dict(), status=201)

    elif request.method == 'GET':
        all_reporters = load_json(REPORTERS_FILE)
        reporter_id = request.GET.get('id')

        if reporter_id:
            for r in all_reporters:
                if r['id'] == int(reporter_id):
                    return JsonResponse(r, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)

        return JsonResponse(all_reporters, safe=False, status=200)


@csrf_exempt
def issues(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if data.get('priority') == 'critical':
            issue = CriticalIssue(
                id=data['id'],
                title=data.get('title', ''),
                description=data.get('description', ''),
                status=data.get('status', ''),
                priority=data['priority'],
                reporter_id=data.get('reporter_id')
            )
        elif data.get('priority') == 'low':
            issue = LowPriorityIssue(
                id=data['id'],
                title=data.get('title', ''),
                description=data.get('description', ''),
                status=data.get('status', ''),
                priority=data['priority'],
                reporter_id=data.get('reporter_id')
            )
        else:
            issue = Issue(
                id=data['id'],
                title=data.get('title', ''),
                description=data.get('description', ''),
                status=data.get('status', ''),
                priority=data.get('priority', ''),
                reporter_id=data.get('reporter_id')
            )

        try:
            issue.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        all_issues = load_json(ISSUES_FILE)
        all_issues.append(issue.to_dict())
        save_json(ISSUES_FILE, all_issues)

        response_data = issue.to_dict()
        response_data['message'] = issue.describe()
        return JsonResponse(response_data, status=201)

    elif request.method == 'GET':
        all_issues = load_json(ISSUES_FILE)
        issue_id = request.GET.get('id')
        status_filter = request.GET.get('status')

        if issue_id:
            for issue in all_issues:
                if issue['id'] == int(issue_id):
                    return JsonResponse(issue, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)

        if status_filter:
            filtered = [i for i in all_issues if i['status'] == status_filter]
            return JsonResponse(filtered, safe=False, status=200)

        return JsonResponse(all_issues, safe=False, status=200)
