import sys
import traceback

import numpy as np
import tellopy
import av
import cv2
# import cv2_.cv2 as cv2
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
                img = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                # with hough circle detection
                img = cv2.medianBlur(img, 5)
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.5, 10000, param1=70, param2=100, minRadius=20, maxRadius=400)
                print(f"CirclesHough: {circles}")
                if circles is not None:
                    for i in circles[0, :]:
                        cv2.circle(gray, (int(i[0]), int(i[1])), int(i[2]), (0, 0, 255), 2) # draw the outer circle
                        cv2.circle(gray, (int(i[0]), int(i[1])), 2, (0, 0, 255), 3) # draw the center of the circle

                cv2.imshow('Hoguh circles', gray)
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
        drone.quit()
        cv2.destroyAllWindows()



if __name__ == '__main__':
    main()