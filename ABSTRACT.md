The authors presented the **_Dark Zurich Dataset_** of 8779 real images comprising 2416 unlabeled nighttime and 2920 unlabeled twilight images with correspondences to their daytime counterparts plus a set of 201 nighttime images with fine pixel-level annotations. The authors used this dataset to feed real data to Map-Guided Curriculum Domain Adaptation (MGCDA) and to create a benchmark with 201 nighttime images for their uncertainty-aware evaluation. The dataset is publicly available.

## Motivation

The field of semantic segmentation has seen rapid advancements in recent years. However, most of the cutting-edge methods are designed for daytime use under optimal lighting conditions. Many outdoor applications, though, demand robust vision systems that can perform reliably at any time of day, in varying lighting conditions, and during inclement weather.

Currently, the dominant approach to addressing perceptual tasks like semantic segmentation involves training deep neural networks with large-scale human annotations. While this supervised learning method has proven highly effective for daytime images, it struggles to scale under adverse conditions such as nighttime. Nighttime poses additional challenges for perceptual tasks due to visual hazards like underexposure, noise, and motion blur, which can corrupt the extracted features.

## Dataset creation

The authors adapted semantic segmentation models from daytime to nighttime, without annotations in the latter domain. To this aim, they propose a new method called Map-Guided Curriculum Domain Adaptation (MGCDA). The underpinnings of MGCDA are threefold: continuity of time, prior knowledge of place, and power of data.

- **Time**: environmental illumination changes continuously from daytime to nighttime. This enables adding intermediate domains between the two to smoothly transfer semantic knowledge.

- **Place**: images taken over different time but with the same 6D camera pose share a large portion of content. The shared content can be used to guide the knowledge transfer process from a favorable condition (daytime) to an adverse condition (nighttime). The authors formalize this observation and propose a method for largescale applications. The method stores the daytime images and the distilled semantic knowledge into a digital map and enhances the semantic nighttime image segmentation by this geo-referenced map in an adaptive fusion framework. This supplement is especially important for nighttime perception as observing partial information and uncertain data is a frequent situation at nighttime.

- **Data**: MGCDA takes advantage of the powerful image translation techniques to stylize real annotated daytime datasets to darker target domains in order to perform standard supervised learning.

Finally, the authors presented Dark Zurich, a dataset of 8779 real images which contains corresponding images of the same driving scenes at daytime, twilight and nighttime. They use this dataset to feed real data to MGCDA and to create a benchmark with 201 nighttime images for our uncertainty-aware evaluation.

## Dataset description

The Dark Zurich was recorded in Zurich using a 1080p GoPro Hero 5 camera, mounted on top of the front windshield of a car. The Dark Zurich dataset was recorded in Zurich using a 1080p GoPro Hero 5 camera mounted on the front windshield of a car. The dataset is divided into one lap for validation, one lap for testing, and the remaining laps, which are unlabeled, for training. This collection includes 3,041 daytime, 2,920 twilight, and 2,416 nighttime images, extracted at a rate of 1 frame per second (fps). These subsets are named Dark Zurich-day, Dark Zurich-twilight, and Dark Zurich-night, respectively.

For the validation and testing night laps, images were extracted at intervals of either 50 meters or 20 seconds, whichever came first. Each nighttime image was paired with a corresponding daytime image to serve as an auxiliary reference. A total of 201 nighttime images (151 from the testing lap and 50 from the validation lap) were annotated with fine pixel-level [Cityscapes](https://www.cityscapes-dataset.com/) labels, including invalid masks, following the authors' protocol. These annotated sets are named Dark Zurich-test and Dark Zurich-val, respectively. In total, 366.8 million pixels were annotated with semantic labels, with 90.2 million pixels marked as invalid.

To validate the quality of the annotations, the authors had 20 images annotated twice by different subjects and measured the consistency. The results showed that 93.5% of the labeled pixels were consistent in the semantic annotations, and 95% were consistent in the invalid masks. Dark Zurich contains fifteen times more annotated nighttime images than [WildDash](https://www.wilddash.cc/), the only other dataset with fine and reliable nighttime annotations. A detailed inspection revealed that approximately 70% of the 345 densely annotated nighttime images in BDD100K contained severe labeling errors, making them unsuitable for evaluation. These errors were particularly prevalent in dark regions, often mislabeled (e.g., the **sky** mislabeled as a **building**). The authors' annotation protocol mitigates such errors by clearly defining invalid regions and using daytime images to assist in the annotation process. This approach ensures that the labeled portion of Dark Zurich serves as a high-quality benchmark, promoting uncertainty-aware evaluation.

<img src="https://github.com/dataset-ninja/dark-zurich/assets/120389559/d745e70f-d6e5-400c-8caf-6880e83331ad" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Qualitative semantic segmentation results on Dark Zurich-test. AdaptSegNet adapts from Cityscapes to Dark Zurich-night.</span>
