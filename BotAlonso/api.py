"""Authentification a slack"""
import aiohttp

from BotAlonso.config import TOKEN


async def api_call(method, data=None, token=TOKEN):
    with aiohttp.ClientSession() as session:
        form = aiohttp.FormData(data or {})
        form.add_field('token', token)

        async with session.post('https://slack.com/api/{0}'.format(method),data=form) as response:
            assert 200 == response.status, ('{0} with {1} failed.'.format(method, data))
            return await response.json()


def api_call1(method, data=None, token=TOKEN):
    with aiohttp.ClientSession() as session:
        form = aiohttp.FormData(data or {})
        form.add_field('token', token)

        with session.post('https://slack.com/api/{0}'.format(method), data=form) as response:
            assert 200 == response.status, ('{0} with {1} failed.'.format(method, data))
            return response.json()