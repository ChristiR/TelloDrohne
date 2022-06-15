import sys
import traceback

import numpy as np
import tellopy
import av
import cv2  # for avoidance of pylint error
import numpy
import time


def main():
    drone = tellopy.Tello()

    try:
        drone.connect()
        drone.wait_for_connection(60.0)

        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        # skip first 300 frames
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                cv2.imshow('Canny', cv2.Canny(image, 100, 200))
                # # #cv2.imshow('Cirlce', cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 100, 20, 100, 30, 5, 200))
                # # #cv2.imshow('Cirlce2', cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 20,param1=50, param2=30, minRadius=0, maxRadius=0))
                # #circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
                # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                # circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
                # if circles is not None:
                #     x = circles[0][0]
                #     y = circles[0][1]
                #     radius = circles[0][2]
                #     cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                # cv2.imshow('Original', image)
                # print(circles)
                # # cimg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                # # circles = np.uint16(np.around(circles))
                # # for i in circles[0, :]:
                # # # draw the outer circle
                # #cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # # # draw the center of the circle
                # #     cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
                # #
                # # cv2.imshow('detected circles', cimg)
                img = image
                img = cv2.medianBlur(img, 5)

                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
                print(f"Circles: {circles}")
                # circles = np.uint16(np.around(circles))
                print(f"Circles2: {circles}")
                if circles is not None:
                    for i in circles[0, :]:
                # draw the outer circle
                        cv2.circle(img, (int(i[0]), int(i[1])), int(i[2]), (0, 255, 0), 2)
                # draw the center of the circle
                        cv2.circle(img, (int(i[0]), int(i[1])), 2, (0, 0, 255), 3)

                cv2.imshow('detected circles', img)
                cv2.waitKey(1)
                if frame.time_base < 1.0 / 60:
                    time_base = 1.0 / 60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time) / time_base)


    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        #drone.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()