import petl as etl
# define some validation constraints
header = ('foo', 'bar', 'baz')
constraints = [
    dict(name='foo must be an int', field='foo', test=int),
    dict(name='bar must be a valid date', field='bar', test=etl.dateparser('%Y-%m-%d')),
    dict(name='baz must be Y or N', field='baz', assertion=lambda v: v in ['Y', 'N']),
    dict(name='not_none', assertion=lambda row: None not in row),
    dict(name='qux_int', field='qux', test=int, optional=True),
]
# now validate a table
table = (('foo', 'bar', 'bazzz'),
         (1, '2000-01-01', 'Y'),
         ('x', '2010-10-10', 'N'),
         (2, '2000/01/01', 'Y'),
         (3, '2015-12-12', 'x'),
         (4, None, 'N'),
         ('y', '1999-99-99', 'z'),
         (6, '2000-01-01'),
         (7, '2001-02-02', 'N', True))
problems = etl.validate(table, constraints=constraints, header=header)
print(problems.lookall())
