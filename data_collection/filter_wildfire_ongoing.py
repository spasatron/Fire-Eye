import tensorflow as tf
import os
import glob
import numpy as np


feature_list = [
    'fire_mask',
    'fire_mask_next_day', 
    'elevation', 
    'wind_direction', 
    'wind_speed', 
    'energy_release_component', 
    'burn_index', 
    'precipitation', 
    'tempature_min', 
    'tempature_max', 
    'drought_index', 
    'vegetation', 
    'population_density'
]
kernel = 64

columns = [
  tf.io.FixedLenFeature(shape=[kernel, kernel], dtype=tf.float32) for _ in feature_list
]
features_dict = dict(zip(feature_list, columns))


def _parse_tfrecordset(proto):
    return tf.io.parse_single_example(proto, features_dict)

def _write_to_tfrecord(writer, record):

    feature_dict = {}
    for feature_name in feature_list:
        feature_dict[feature_name] = tf.train.Feature(
            float_list=tf.train.FloatList(
                value=record[feature_name].numpy().reshape(-1)))
    tf_example = tf.train.Example(
        features=tf.train.Features(feature=feature_dict))
    writer.write(tf_example.SerializeToString())


def _write_ongoinging_dataset(parsed_data):

    compression_type = tf.io.TFRecordOptions(compression_type='GZIP')
    ongoing_writer = tf.io.TFRecordWriter('FireEyeData.tfrecord.gz', options=compression_type)
    #fire_index = feature_list.index('fire_mask')
    for record in parsed_data:
        # Filter Data Here
        if np.amax(record['fire_mask'].numpy()) == 2:
            _write_to_tfrecord(ongoing_writer, record)


def main():
    data_folder = 'data_collection/unfiltered_data'
    # List all files in the folder

    file_pattern = 'FireData_*.tfrecord.gz'

    # List all files that match the pattern
    tfrecord_files = glob.glob(os.path.join(data_folder, file_pattern))

    # Load all TFRecord files into a single dataset
    raw_dataset = tf.data.TFRecordDataset(tfrecord_files, compression_type="GZIP")

    parsed_data = raw_dataset.map(_parse_tfrecordset)

    _write_ongoinging_dataset(parsed_data)


if __name__ == "__main__":

    main()