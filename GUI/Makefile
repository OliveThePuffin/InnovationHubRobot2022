SHELL:=/bin/bash
CC:=g++
SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin

EXE := $(BIN_DIR)/TGUI
SRC := $(wildcard $(SRC_DIR)/*.cpp)
OBJ := $(SRC:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

CPPFLAGS := -Iinclude `pkg-config --cflags --libs gtkmm-3.0` -MMD -MP
CFLAGS   := -Wall
LDFLAGS  := -Llib
LDLIBS   := -lm
.PHONY: all clean

all: $(EXE)

exec: all
	bin/TGUI

$(EXE): $(OBJ) | $(BIN_DIR)
	$(CC) $(CPPFLAGS) $(LDFLAGS) $^ $(LDLIBS) -o $@
	@$(RM) $(EXE).d

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

$(BIN_DIR) $(OBJ_DIR):
	mkdir -p $@

clean:
	@$(RM) -rv $(BIN_DIR) $(OBJ_DIR)
	@$(RM) $(EXE)

#-include $(OBJ:.o=.d)


