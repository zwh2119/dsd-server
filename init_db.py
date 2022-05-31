import db.admin
import db.device

print('Add admin to db')
db.admin.add('jokers', 'dsd_jokers')
db.admin.add('zwh', 'dsd2022')

print('Add device to db')
db.device.get('b6ef61bf-facf-4878-bd6f-d271324fa0e7')
db.device.get('dfc2742d-c5cd-affc-abb3-d888a1e30515')
db.device.get('f1d717df-8458-fa90-3f3e-db126152e345')
db.device.get('7896f3e0-e970-18b7-a6ed-d4c6e66916a4')
