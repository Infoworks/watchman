from utils import mongo


def create_domain(domain_name='TestDomain'):
    domain_doc = mongo.client.domains.find_one({'name': domain_name})
    if domain_doc:
        print 'Domain exists.'
        domain_id = domain_doc['_id']
        create_domain_sources(domain_id)
    else:
        print 'Creating TestDomain.'
        new_domain = {
            'name': domain_name,
            'description': 'Test Domain',
        }
        domain_id = mongo.client.domains.insert(new_domain)
        create_domain_sources(domain_id)

    # Make domain accessible to all users
    mongo.client.users.update({}, {'$addToSet': {'accessible_domains': domain_id}}, multi=True, upsert=True)

    print 'Domain setup completed!'


def create_domain_sources(domain_id):
    domain_sources_doc = mongo.client.domain_sources.find_one({'domain': domain_id})

    if domain_sources_doc is None:  # no document
        print 'Creating domain_sources document.'
        domain_sources_doc = {
            'domain': domain_id,
            'sources': [],
        }
        mongo.client.domain_sources.insert(domain_sources_doc)


create_domain()
