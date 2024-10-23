from database import fetch_staff_embeddings, load_staff, get_staff_info, get_all_zone, insert_zone
from database import get_all_track
from database.staff_operations import delete_staff

# staff_embeddings = fetch_staff_embeddings()
# print(staff_embeddings)
delete_staff('56651133-59e5-42f6-8550-a95414f1f596')

staff = load_staff()
for row in staff:
    print(row)

# info = get_staff_info(id = "c477df85-b76e-4347-8a2d-7ee9a1161e1c")
# print(info)

# insert_zone(80, 220, 40, 180, 380, 460, 460, 280)

tracks = get_all_track()
print(tracks)