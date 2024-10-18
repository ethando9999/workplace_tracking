from database import fetch_staff_embeddings, load_staff, get_staff_info, get_all_zone, insert_zone

# staff_embeddings = fetch_staff_embeddings()
# print(staff_embeddings)

# staff = load_staff()
# for row in staff:
#     print(row)

# info = get_staff_info(id = "c477df85-b76e-4347-8a2d-7ee9a1161e1c")
# print(info)

insert_zone(80, 220, 40, 180, 380, 460, 460, 280)
zones = get_all_zone()
print(zones)