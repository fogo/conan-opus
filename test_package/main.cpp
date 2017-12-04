#include <opus.h>
#include <iostream>

int main(int argc, char** argv) {
    int error = 0;
    OpusEncoder *enc = opus_encoder_create(8000/*Hz*/, 1/*mono*/, OPUS_APPLICATION_VOIP, &error);
    std::cout << "opus enc at " << enc << ", error code is " << error << std::endl;
    OpusDecoder *dec = opus_decoder_create(8000/*Hz*/, 1/*mono*/, &error);
    std::cout << "opus dec at " << dec << ", error code is " << error << std::endl;

    return 0;
}
