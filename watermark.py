# watermark.py - placeholder watermark removal
import shutil

def remove_watermark(input_path, output_path):
    try:
        shutil.copyfile(input_path, output_path)
        return True
    except Exception as e:
        print('remove_watermark error:', e)
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3:
        ok = remove_watermark(sys.argv[1], sys.argv[2])
        print('done', ok)
    else:
        print('Usage: python watermark.py input.jpg output.jpg')
