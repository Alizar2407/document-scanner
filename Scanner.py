import numpy as np
from PIL import Image
import cv2


class Scanner:
    @staticmethod
    def scan(image, template, orb_features_number=500, matches_percentage=5):
        # Convert images from PIL to cv2
        if isinstance(image, Image.Image):
            image = np.array(image)
        if isinstance(template, Image.Image):
            template = np.array(template)

        # Convert images to grayscale
        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

        # Detect ORB features and compute descriptors
        orb = cv2.ORB_create(orb_features_number)
        image_keypoints, image_descriptors = orb.detectAndCompute(image_gray, None)
        template_keypoints, template_descriptors = orb.detectAndCompute(
            template_gray, None
        )

        # ----------------------------------------------------------------
        # Find matching features
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
        matches = list(matcher.match(template_descriptors, image_descriptors, None))

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Leave only best matches
        numGoodMatches = int(len(matches) * matches_percentage / 100)
        matches = matches[:numGoodMatches]

        # Draw best matches
        matches_image = cv2.drawMatches(
            image, image_keypoints, template, template_keypoints, matches, None
        )

        # Convert from cv2 to PIL
        matches_image = Image.fromarray(matches_image)

        if len(matches) < 4:
            return None, matches_image, "Found less than 4 matches"

        # ----------------------------------------------------------------
        # Extract locations of filtered matches
        template_points = np.zeros((len(matches), 2), dtype=np.float32)
        image_points = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            template_points[i, :] = template_keypoints[match.queryIdx].pt
            image_points[i, :] = image_keypoints[match.trainIdx].pt

        # Find homography
        h, mask = cv2.findHomography(
            image_points, template_points, cv2.RANSAC
        )  # RANSAC - RANdom SAmple Consequences

        # ----------------------------------------------------------------
        # Use homography to warp image
        height, width, channels = image.shape
        scanned_image = cv2.warpPerspective(image, h, (width, height))

        # Convert from cv2 to PIL
        scanned_image = Image.fromarray(scanned_image)

        # ----------------------------------------------------------------

        return scanned_image, matches_image, None
