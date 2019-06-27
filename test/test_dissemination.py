#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import logging
import time

first = 33001
count = 10
servers_list = range(first, first+count)


def test_discover_join(servers, helpers):
    t1 = time.time()

    for port, srv in servers.items():
        assert servers[first].probe_uri('localhost:{}'.format(port))

    t2 = time.time()
    logging.warn('Probe all in {:.3f}s'.format(t2-t1))

    servers_copy = {**servers}
    def check_fullmesh():
        for port, srv in list(servers_copy.items()):
            members = srv.members()
            alive = [uri for uri, member in members.items() if member['status'] == 'alive']
            logging.info('Member {} sees {} others'.format(port, len(alive)))
            if len(alive) == len(servers_list):
                del servers_copy[port]

        logging.info('{}/{} ready so far'.format(
            len(servers_list)-len(servers_copy),
            len(servers_list)
        ))
        assert not servers_copy

    helpers.wait_for(check_fullmesh, timeout=1500)

    t3 = time.time()
    logging.warn('Full mesh in {:.3f}s'.format(t3-t2))

def test_discoder_kill(servers, helpers):

    logging.warning('Killing localhost:{}'.format(first))
    servers[first].kill()
    del servers[first]

    servers_copy = {**servers}
    uri = 'localhost:{}'.format(first)
    def check_public_opinion():
        """ Cheack that all members consider URI has given STATUS """

        for port, srv in list(servers_copy.items()):
            member = srv.get_member(uri)
            if member != None and member['status'] == 'dead':
                del servers_copy[port]

        assert not servers_copy

    helpers.wait_for(check_public_opinion, timeout=5)
