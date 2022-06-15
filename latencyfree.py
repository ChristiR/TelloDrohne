# import threading
# import tellopy
# import cv2
# import numpy
# import image
# import av
# def video_thread():
#     global drone
#     global run_video_thread
#     global av
#     print('START Video thread')
#     drone.start_video()
#     try:
#         container = av.open(drone.get_video_stream())
#         frame_count = 0
#         while True:
#             for frame in container.decode(video=0):
#                 frame_count = frame_count + 1
#                 image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
#                 cv2.imshow('Original', image)
#                 cv2.waitKey(1)
#         cv2.destroyWindow('Original')
#     except KeyboardInterrupt as e:
#         print('KEYBOARD INTERRUPT Video thread ' + e)
#     except Exception as e:
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         print('EXCEPTION Video thread ' + e)
#
#
# def main():
#     global drone
#     drone = tellopy.Tello()
#     #drone.port = 8889
#     #drone.tello_addr = ('192.168.10.1', 8889)
#     drone.connect()
#     #print("wifi strength: " + str(drone.wifi_strength))
#
#     try:
#         threading.Thread(target=video_thread).start()
#
#     except e:
#         print(str(e))
#     finally:
#         print('Shutting down connection to drone...')
#         drone.quit()
#         exit(1)
#
#
# if __name__ == '__main__':
#     main()

import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
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
                cv2.imshow('Original', image)
                cv2.imshow('Canny', cv2.Canny(image, 100, 200))
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