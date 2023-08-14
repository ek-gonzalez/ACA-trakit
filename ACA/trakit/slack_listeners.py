import logging

from slack_bolt import App
from decouple import config
from .models import Suser, Task, Pair, Project
from slack_sdk import WebClient

client = WebClient(token=config('SLACK_BOT_OAUTH'))

logger = logging.getLogger(__name__)

true = True

app = App(
    token=config('SLACK_BOT_OAUTH'),
    signing_secret=config('SLACK_SIGNING_SECRET'),
    token_verification_enabled=False,
    process_before_response=True,
)

def suserExists(user):
    return Suser.objects.filter(id=user).first()


def get_projects(user):
    projects = set()
    for pair in getAllPairs(user):
        projects = projects.union(Project.objects.filter(members_pair=pair))
    return projects



@app.shortcut("new_trak")
def modal_new_trak(ack, body, logger, client):
    ack()
    suser = assertSuser(body["user"]["id"])
    options = []
    for project in get_projects(suser):
        option = {}
        option["text"] = {}
        option["text"]["type"] = "plain_text"
        option["text"]["text"] = project.name
        option["value"] = str(project.id)
        options.append(option)

    view = {
	"type": "modal",
	"callback_id": "new_trak",
	"title": {
		"type": "plain_text",
		"text": "Add new trak",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "input",
			"block_id": "trak_name_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "trak_name_input",
				"placeholder": {
					"type": "plain_text",
					"text": "Write a simple description of the trak",
					"emoji": true
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Trak name",
				"emoji": true
			}
		},
		{
			"type": "input",
			"block_id": "project_select_block",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select the project you want to add the trak to",
					"emoji": true
				},
				"options": options,
				"action_id": "select_project"
			},
			"label": {
				"type": "plain_text",
				"text": "Project",
				"emoji": true
			}
		},
		{
			"type": "input",
			"block_id": "description_new_trak",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "description_new_trak_text"
			},
			"label": {
				"type": "plain_text",
				"text": "Update request response",
				"emoji": true
			}
		}
	]
}

    client.views_open(
        trigger_id=body["trigger_id"],
        view=view
        )



def registerSuser(user):
    suser = Suser()
    suser.id = user
    suser.save()


def assertSuser(user):
    if not suserExists(user):
        registerSuser(user)
    return suserExists(user)


@app.shortcut("retrieve_traks")
def modal_retrieve_traks(ack, body, logger, client):
    ack()
    suser = assertSuser(body["user"]["id"])
    options = []
    for project in get_projects(suser):
        option = {}
        option["text"] = {}
        option["text"]["type"] = "plain_text"
        option["text"]["text"] = project.name
        option["value"] = str(project.id)
        options.append(option)
    view = {
	"type": "modal",
	"callback_id": "see_traks",
	"title": {
		"type": "plain_text",
		"text": "See my traks",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "divider"
		},
		{
			"type": "input",
			"block_id": "project_select_block_rt",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select the project to see its traks",
					"emoji": true
				},
				"options": options,
				"action_id": "project_rt"
			},
			"label": {
				"type": "plain_text",
				"text": "Project",
				"emoji": true
			}
		}
	]
}
    client.views_open(
        trigger_id=body["trigger_id"],
        view=view
        )


@app.action("new_project")
def modal_new_project(ack, body, logger, client):
    ack()
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
	"type": "modal",
	"private_metadata": body["actions"][0]["value"],
	"callback_id": "project_details",
	"title": {
		"type": "plain_text",
		"text": "Trakit",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Let's create a new project! :smile:",
				"emoji": true
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"block_id": "name_block",
			"element": {
				"type": "plain_text_input",
				"action_id": "project-name",
				"placeholder": {
					"type": "plain_text",
					"text": "How do you want to call this project?",
					"emoji": true
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Project name",
				"emoji": true
			}
		},

	]
}
    )


@app.view("see_traks")
def handle_submission(ack, body, client, view, logger):
    suser = assertSuser(body["user"]["id"])
    project = Project.objects.get(id=int(view["state"]["values"]["project_select_block_rt"]["project_rt"]["selected_option"]["value"]))
    tasks = Task.objects.filter(project=project)
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Your traks: {project.name}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]

    for task in tasks:
        section = {}
        section["type"] = "section"
        section["text"] = {}
        section["text"]["type"] = "mrkdwn"
        section["text"]["text"] = f"*{task.name}*\n{task.description}"
        button = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "action_id": "request_update",
                    "text": {
                        "type": "plain_text",
                        "text": "Request update"
                    },
                    "style": "primary",
                    "value": str(task.id)
                }
            ]
        }
        blocks.append(section)
        blocks.append(button)

    result = client.chat_postMessage(
        channel=suser.id,
        blocks=blocks,
        text="Traks requested"
        # You could also use a blocks[] array to send richer content
    )
    logger.info(result)
    ack()


@app.view("send_response")
def send_response(ack, body, say, logger, view):
    ack()
    suser = assertSuser(body["user"]["id"])

    task = Task.objects.get(id=int(view["private_metadata"]))
    member1 = task.project.members_pair.member1
    member2 = task.project.members_pair.member2
    if suser == member1:
        to = member2
    else:
        to = member1
    ms = view["state"]["values"]["update_block"]["update_text"]["value"]
    result = client.chat_postMessage(channel=to.id,
                                     text=f"*<@{suser.id}> just sent you an update about _trak_: {task.name}*\n{ms}")
    result = client.chat_postMessage(channel=suser.id,
                                     text=f"Great! I sent your response to the request to <@{to.id}>")
    logger.info(result)





@app.action("send_reply")
def send_reply(ack, body, logger, say, event):
    ack()
    suser = assertSuser(body["user"]["id"])
    task = Task.objects.get(id=int(body["actions"][0]["value"]))
    view = {
	"type": "modal",
	"callback_id": "send_response",
	"private_metadata": body["actions"][0]["value"],
	"title": {
		"type": "plain_text",
		"text": "Response to request",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"<@{suser.id}> requested an update for the _trak_: {task.name}"
			}
		},
		{
			"type": "input",
			"block_id": "update_block",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "update_text"
			},
			"label": {
				"type": "plain_text",
				"text": "Update request response",
				"emoji": true
			}
		}
	]
    }
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view=view)



@app.action("request_update")
def request_update(ack, body, logger, client, say, event):
    ack()
    suser = assertSuser(body["user"]["id"])
    task = Task.objects.get(id=int(body["actions"][0]["value"]))
    say("Cool! Update requested!")
    blocks = [{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"Hey! :wave: <@{suser.id}> requested an update for the _trak_: {task.name}"
			}}]
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "action_id": "send_reply",
                "text": {
                    "type": "plain_text",
                    "emoji": true,
                    "text": "Send reply"
                },
                "style": "primary",
                "value": str(task.id)
            },
            {
                "type": "button",
                "action_id": "no_updates",
                "text": {
                    "type": "plain_text",
                    "emoji": true,
                    "text": "No updates so far"
                },
                "style": "danger",
                "value": str(task.id)
            }
        ]
    })


    member1 = task.project.members_pair.member1
    member2 = task.project.members_pair.member2
    if suser == member1:
        to = member2
    else:
        to = member1
    result = client.chat_postMessage(
        channel=to.id,
        blocks=blocks,
        text="Update request"
        # You could also use a blocks[] array to send richer content
    )
    logger.info(result)







@app.view("project_details")
def handle_submission_project(ack, body, client, view, logger):
    suser = assertSuser(body["user"]["id"])
    project = Project()
    pair = Pair.objects.get(id=int(view["private_metadata"]))
    project.members_pair = pair
    project.name = view["state"]["values"]["name_block"]["project-name"]["value"]
    project.save()
    if suser == pair.member1:
        other = pair.member2
    else:
        other = pair.member1
    blocks = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"Great! Project \"{project.name}\" has been created! :white_check_mark:"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"Now, you will be able to create _traks_ with <@{other.id}> :raised_hands:"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "A _trak_ can be anything you'd like to track along your huddles with your colleague! Here are some examples:\n\n• You told your colleague you would research about a new technology that could be implemented in a product. \n • Your colleague made some mistake on the last report he/she/they sent you. You need a corrected version ASAP! \n • You agreed to think about new solutions for a specific problem for the next time you get in a huddle together."
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Whenever you want to add a trak to the project, use the :shortcut_dark: button :arrow_down:!"
			}
		}
	]
    result = client.chat_postMessage(
        channel=suser.id,
        blocks=blocks,
        text="New project created!"
        # You could also use a blocks[] array to send richer content
    )
    logger.info(result)
    ack()


@app.view("new_trak")
def handle_submission_trak(ack, body, client, view, logger):
    suser = assertSuser(body["user"]["id"])
    task = Task()
    task.name = view["state"]["values"]["trak_name_block"]["trak_name_input"]["value"]
    task.description = view["state"]["values"]["description_new_trak"]["description_new_trak_text"]["value"]
    task.project = Project.objects.get(id=int(view["state"]["values"]["project_select_block"]["select_project"]["selected_option"]["value"]))
    task.save()
    result = client.chat_postMessage(
        channel=suser.id,
        text="New task created!"
        # You could also use a blocks[] array to send richer content
    )
    logger.info(result)
    ack()


@app.event("app_mention")
def handle_app_mentions(logger, event, say):
    logger.info(event)
    if not suserExists(event['user']):
        say(f"You're new, <@{event['user']}>!")
        registerSuser(event['user'])
    else:
        say(f"I know you, <@{event['user']}>")



@app.event("user_huddle_changed")
def handle_huddle_status(logger, event, say, ack):
    ack()
    logger.info(event)
    suser = assertSuser(event['user']['id'])
    suser.inHuddle = event['user']['profile']['huddle_state'] == 'in_a_huddle'
    suser.save()

    if suser.inHuddle:
        pair = searchPair(suser)
        if not pair:
            connected = Suser.objects.filter(inHuddle=True)
            if connected.count() == 2:
                pair = Pair()
                pair.member1 = connected.first()
                pair.member2 = connected.last()
                pair.save()
        if pair:
            if pair.member1.id == suser.id:
                other = pair.member2
            else:
                other = pair.member1

            projects = Project.objects.filter(members_pair__member1=suser).filter(members_pair__member2=other)
            projects = projects.union(Project.objects.filter(members_pair__member1=other).filter(members_pair__member2=suser))
            if not projects:
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hey <@{suser.id}>! :wave:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"It looks like this is your first time in a huddle with <@{other.id}>! :smile_cat:\n I can help you keep track :railway_track: of your meetings so when you connect again you can start right where you left it! :magic_wand:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Once you create a project, you will be able to add tasks to it and track their progress, even when you're not in a huddle! :raised_hands:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Go ahead and track your first project with <@{other.id}>!"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "value": str(pair.id),
                                "text": {
                                    "type": "plain_text",
                                    "text": "Create project",
                                    "emoji": True
                                },
                                "style": "primary",
                                "action_id": "new_project"
                            }
                        ]
                    }
                ]
            else:
                tasks = Task.objects.filter(project__members_pair__member1=suser)
                tasks = tasks.union(Task.objects.filter(project__members_pair__member2=suser))
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"It looks like you're in a huddle with <@{other.id}>! Let me show you your traks:"
                        }
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Your traks: ",
                            "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]
                for task in tasks:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{task.name}*\n{task.description}"
                        }
                    })
                    blocks.append(
		            {
		            	"type": "divider"
	            	})

            result = client.chat_postMessage(
                channel=suser.id,
                blocks=blocks,
                text="We detected a new huddle!"
            )
            logger.info(result)

    ack()


def getAllPairs(user):
    asMember1 = Pair.objects.filter(member1=user)
    asMember2 = Pair.objects.filter(member2=user)
    return asMember1.union(asMember2)


def searchPair(user):
    asMember1 = Pair.objects.filter(member1=user)
    for pair in asMember1:
        if not pair.member2.inHuddle:
            asMember1 = asMember1.exclude(member2__id=pair.member2.id)
    asMember2 = Pair.objects.filter(member2=user)
    for pair in asMember2:
        if not pair.member1.inHuddle:
            asMember2 = asMember2.exclude(member1__id=pair.member1.id)
    return asMember1.union(asMember2).first()
