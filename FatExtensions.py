from FatEntity import FatEntity
from FatHandler import FatHandler


def get_info_about_fragmentation(fat_handler: FatHandler):
    incorrect_clusters = 0
    count = 0
    for cluster in range(fat_handler.fat_entity.clusters_count):
        val_clus = fat_handler.get_cluster_value_in_main_fat(cluster)
        if val_clus == 0:
            continue
        count += 1
        if fat_handler.is_final_cluster(val_clus):
            continue
        if val_clus != cluster + 1:
            print(cluster)
            incorrect_clusters += 1

    return incorrect_clusters * 100 / count


def find_empty_clusters(cluster_number: int, fat_entity: FatEntity, indexed_table: dict):
    result = []
    for i in range(2, fat_entity.clusters_count):
        if len(result) == cluster_number:
            break
        if i not in indexed_table:
            result.append(i)
    else:
        if len(result):
            return None

    return result
