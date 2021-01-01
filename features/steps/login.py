import json

from behave import *

from features.environment import login_details_file
from common import open_tab, window_id


# @given('')
# def step_impl(context):
#     pass

@given('login details')
def step_impl(context):
    with open(login_details_file) as f:
        context.data = json.load(f)


@then('portal is reachable')
def step_impl(context):
    if context.data['0']['insname'] == "Apollo Munich Health Insurance Co. Ltd":
        window_id = tab_id = open_tab(context.browser, context.main_window)
        from portals.apollo import pre_login
        pre_login(context.data['0']['PortalLink'], tab_id, context.browser)


@when('username is filled')
def step_impl(context):
    tab_id = window_id
    if context.data['0']['insname'] == "Apollo Munich Health Insurance Co. Ltd":
        from portals.apollo import fill_username
        fill_username(context.data['0']['PortalUser'], tab_id, context.browser)


@when('password is filled')
def step_impl(context):
    tab_id = window_id
    if context.data['0']['insname'] == "Apollo Munich Health Insurance Co. Ltd":
        from portals.apollo import fill_password
        fill_password(context.data['0']['PortalPass'], tab_id, context.browser)


@when('pressed login button')
def step_impl(context):
    tab_id = window_id
    if context.data['0']['insname'] == "Apollo Munich Health Insurance Co. Ltd":
        from portals.apollo import press_login
        press_login(tab_id, context.browser)


@then('login is successful')
def step_impl(context):
    tab_id = window_id
    if context.data['0']['insname'] == "Apollo Munich Health Insurance Co. Ltd":
        from portals.apollo import check_if_logged_in
        check_if_logged_in(tab_id, context.browser)