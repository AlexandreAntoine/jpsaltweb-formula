"""
Ce module a pour objectif d'être l'api personalise de John Paul pour SaltStack
"""

import logging

log = logging.getLogger(__name__)

import re

##
## 
##
def info():
    """
    Get all application information
    """
    ret = {}

    applications_grains = __grains__['applications']
    applications_pillar = __salt__['pillar.get']('applications')

    for app in applications_pillar:
        if app in applications_grains:
            if app not in ret:
                ret[app] = {}
            for env in applications_pillar[app]:
                if env in applications_grains[app]:
                    if env not in ret[app]:
                        ret[app][env] = list()
                    for repo in applications_pillar[app][env]:
                        tmp = None
                        repo_id = "None"
                        extpillar = False
                        if 'repo_id' in repo:
                            repo_id = repo['repo_id']
                        if 'extpillar_used' in repo:
                            extpillar = repo['extpillar_used']
                        if repo['type'] == 'git':
                            # if 'rev' in repo:
                            #     tmp = __salt__['git.revision'](repo['target'],
                            #                                    repo['rev'])
                            # else:
                            try:
                                tmp = __salt__['git.revision'](repo['target'])
                            except:
                                tmp = ""
                        if repo['type'] == 'svn':
                            tmp =  re.search('Revision: (.+)',
                                             __salt__['svn.info'](repo['target']),
                                             re.MULTILINE).group(1)
                        if tmp != "":
                            ret[app][env].append({repo['type']: [tmp, repo['target'], repo_id, extpillar]})

    return ret # applications_grains

def git_rev(cwd, rev):
    """
    Update git repo to rev
    """

    return __salt__['git.checkout'](cwd, rev)
