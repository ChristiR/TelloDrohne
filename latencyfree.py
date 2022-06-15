import threading
import tellopy
import cv2
import numpy
import image
import av
def video_thread():
    global drone
    global run_video_thread
    global av
    print('START Video thread')
    drone.start_video()
    try:
        container = av.open(drone.get_video_stream())
        frame_count = 0
        while True:
            for frame in container.decode(video=0):
                frame_count = frame_count + 1
                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                cv2.imshow('Original', image)
                cv2.waitKey(1)
        cv2.destroyWindow('Original')
    except KeyboardInterrupt as e:
        print('KEYBOARD INTERRUPT Video thread ' + e)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('EXCEPTION Video thread ' + e)


def main():
    global drone
    drone = tellopy.Tello()
    drone.port = 8889
    drone.tello_addr = ('192.168.10.1', 8889)
    drone.connect()
    print("wifi strength" + drone.wifi_strength)

    try:
        threading.Thread(target=video_thread).start()

    except e:
        print(str(e))
    finally:
        print('Shutting down connection to drone...')
        #drone.quit()
        exit(1)


if __name__ == '__main__':
    main()