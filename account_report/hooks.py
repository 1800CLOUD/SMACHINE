
def post_init_hook(cr, result):
    query = '''
    update account_account aa
    set group_id = ag.id
    from account_group ag
    where ag.code = left(aa.code, -2);
    '''
    cr.execute(query)

    query = '''
    update account_group ag
    set parent_id = agp.id
    from account_group agp
    where agp.code = left(ag.code, -2)
    and ag.id != agp.id;
    '''
    cr.execute(query)

    query = '''
    update account_group ag
    set parent_id = agp.id
    from account_group agp
    where agp.code = left(ag.code, -1)
    and ag.id != agp.id
    and length(ag.code) = 2;
    '''
    cr.execute(query)
