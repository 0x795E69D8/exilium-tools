CXX = g++
CXXFLAGS = -std=c++17 -Wall -O2 -pthread -Iinclude
SRCS = src/main.cpp src/crypto.cpp src/file_io.cpp src/verify.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = gf2_ab_decrypt

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) $(TARGET).exe