import os
import shutil, glob, csv
import numpy as np

import supervisely as sly
from supervisely.io.fs import (
    file_exists,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # Possible structure for bbox case. Feel free to modify as you needs.

    train_data_path = "/home/alex/DATASETS/IMAGES/Dark Zurich/Dark_Zurich_train_anon"
    val_data_path = "/home/alex/DATASETS/IMAGES/Dark Zurich/Dark_Zurich_val_anon"
    test_data_path = "/home/alex/DATASETS/IMAGES/Dark Zurich/Dark_Zurich_test_anon_withoutGt"

    ds_name_to_data = {"val": val_data_path, "train": train_data_path, "test": test_data_path}

    images_ext = "_rgb_anon.png"
    masks_ext = "_gt_labelColor.png"

    group_tag_name = "corresp"

    batch_size = 10


    def get_unique_colors(img):
        unique_colors = []
        img = img.astype(np.int32)
        h, w = img.shape[:2]
        colhash = img[:, :, 0] * 256 * 256 + img[:, :, 1] * 256 + img[:, :, 2]
        unq, unq_inv, unq_cnt = np.unique(colhash, return_inverse=True, return_counts=True)
        indxs = np.split(np.argsort(unq_inv), np.cumsum(unq_cnt[:-1]))
        col2indx = {unq[i]: indxs[i][0] for i in range(len(unq))}
        for col, indx in col2indx.items():
            if col != 0:
                unique_colors.append((col // (256**2), (col // 256) % 256, col % 256))

        return unique_colors


    def create_ann(image_path):
        labels = []
        tags = []

        img_wight = 1920
        img_height = 1080

        image_name = get_file_name(image_path)

        seq_value = image_path.split("/")[-2]
        seq_tag = sly.Tag(seq_meta, value=seq_value)
        tags.append(seq_tag)

        gps_values = name_to_gps[image_name]
        latitude_tag = sly.Tag(latitude_meta, value=gps_values[0])
        tags.append(latitude_tag)

        longitude_tag = sly.Tag(longitude_meta, value=gps_values[1])
        tags.append(longitude_tag)

        daytime_value = image_path.split("/")[-3]
        daytime_tag = sly.Tag(daytime_meta, value=daytime_value)
        tags.append(daytime_tag)

        if ds_name == "train":
            corresp_tag_value = name_to_corresp_tag.get(image_name)
        else:
            corresp_tag_value = image_name.split("_")[0] + "_" + image_name.split("_")[2]

        if corresp_tag_value is not None:
            corresp_tag = sly.Tag(group_tag_meta, value=corresp_tag_value)
            tags.append(corresp_tag)

        if ds_name == "val":
            mask_path = image_path.replace(images_ext, masks_ext)
            mask_path = mask_path.replace("rgb_anon", "gt")

            if file_exists(mask_path):
                mask_np = sly.imaging.image.read(mask_path)
                unique_colors = get_unique_colors(mask_np)
                for color in unique_colors:
                    mask = np.all(mask_np == color, axis=2)
                    bitmap = sly.Bitmap(data=mask)
                    obj_class = color_to_obj_class.get(color)
                    if obj_class is not None:
                        label = sly.Label(bitmap, obj_class)
                        labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)


    city_classes_to_colors = {
    # "unlabeled": (0, 0, 0),
    # "ego vehicle": (98, 15, 138),
    # "rectification border": (15, 120, 55),
    # "out of roi": (125, 138, 15),
    # "static": (63, 15, 138),
    # "dynamic": (111, 74, 0),
    # "ground": (81, 0, 81),
    "road": (128, 64, 128),
    "sidewalk": (244, 35, 232),
    #"parking": (250, 170, 160),
    #"rail track": (230, 150, 140),
    "building": (70, 70, 70),
    "wall": (102, 102, 156),
    "fence": (190, 153, 153),
    #"guard rail": (180, 165, 180),
    #"bridge": (150, 100, 100),
    #"tunnel": (150, 120, 90),
    "pole": (153, 153, 153),
    "traffic light": (250, 170, 30),
    "traffic sign": (220, 220, 0),
    "vegetation": (107, 142, 35),
    "terrain": (152, 251, 152),
    "sky": (70, 130, 180),
    "person": (220, 20, 60),
    "rider": (255, 0, 0),
    # "car": (0, 0, 142),
    # "truck": (0, 0, 70),
    "truck": (91, 91, 136),
    # "bus": (0, 60, 100),
    "bus": (91, 130, 155),
    #"caravan": (0, 0, 90),
    #"trailer": (0, 0, 110),
    "train": (0, 80, 100),
    "motorcycle": (0, 0, 230),
    "bicycle": (119, 11, 32),
    "car": (0, 0, 142),
}

    obj_classes = []
    color_to_obj_class = {}

    for class_name, color in city_classes_to_colors.items():
        obj_class = sly.ObjClass(class_name, sly.Bitmap, color=color)
        obj_classes.append(obj_class)
        color_to_obj_class[color] = obj_class

    latitude_meta = sly.TagMeta("latitude", sly.TagValueType.ANY_STRING)
    longitude_meta = sly.TagMeta("longitude", sly.TagValueType.ANY_STRING)
    daytime_meta = sly.TagMeta(
        "daytime", sly.TagValueType.ONEOF_STRING, possible_values=["day", "night", "twilight"]
    )
    seq_meta = sly.TagMeta("sequence", sly.TagValueType.ANY_STRING)

    group_tag_meta = sly.TagMeta(group_tag_name, sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    meta = sly.ProjectMeta(
        obj_classes=obj_classes,
        tag_metas=[latitude_meta, longitude_meta, group_tag_meta, daytime_meta, seq_meta],
    )
    api.project.update_meta(project.id, meta.to_json())
    api.project.images_grouping(id=project.id, enable=True, tag_name=group_tag_name)

    for ds_name, ds_data in ds_name_to_data.items():

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        name_to_corresp_tag = {}
        name_to_gps = {}

        if ds_name == "train":
            corresp_files = glob.glob(ds_data + "/corresp/*/*/*/*.csv")
            for corresp_file in corresp_files:
                with open(corresp_file, "r") as file:
                    csvreader = csv.reader(file)
                    for row in csvreader:
                        tag_value = (
                            get_file_name(row[0]).replace("_frame_", "_")
                            + "_"
                            + get_file_name(row[1]).replace("_frame_", "_")
                        )
                        name_to_corresp_tag[get_file_name(row[0]) + "_rgb_anon"] = tag_value
                        name_to_corresp_tag[get_file_name(row[1]) + "_rgb_anon"] = tag_value

        gps_files = glob.glob(ds_data + "/gps/*/*/*/*.csv")
        for gps_file in gps_files:
            with open(gps_file, "r") as file:
                csvreader = csv.reader(file)
                for row in csvreader:
                    name_to_gps[get_file_name(row[0]) + "_rgb_anon"] = row[1:]

        images_pathes = glob.glob(ds_data + "/rgb_anon/*/*/*/*.png")

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

        for images_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
            img_names_batch = [get_file_name_with_ext(image_path) for image_path in images_pathes_batch]

            anns_batch = [create_ann(image_path) for image_path in images_pathes_batch]

            img_infos = api.image.upload_paths(dataset.id, img_names_batch, images_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            api.annotation.upload_anns(img_ids, anns_batch)

            progress.iters_done_report(len(images_pathes_batch))

    return project
