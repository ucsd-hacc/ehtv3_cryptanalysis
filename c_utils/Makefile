CC = /usr/bin/gcc
REF_DIR = ehtv3l1
CFLAGS = -g -O3 -std=c99 -I $(REF_DIR)
LDFLAGS = -static-libgcc -lssl -lcrypto -lm

REF_SOURCES = $(REF_DIR)/sign.c $(REF_DIR)/eht_keygen.c $(REF_DIR)/eht_siggen.c $(REF_DIR)/eht_sigver.c $(REF_DIR)/keccak.c $(REF_DIR)/tables.c $(REF_DIR)/parameters.c $(REF_DIR)/rng.c $(REF_DIR)/general_functions.c $(REF_DIR)/general_functions_with_tables.c
REF_HEADERS = $(REF_DIR)/api.h $(REF_DIR)/eht_keygen.h $(REF_DIR)/eht_siggen.h $(REF_DIR)/eht_sigver.h $(REF_DIR)/keccak.h $(REF_DIR)/tables.h $(REF_DIR)/parameters.h $(REF_DIR)/rng.h $(REF_DIR)/general_functions.h $(REF_DIR)/general_functions_with_tables.h

SOURCES = common.c
HEADERS = common.h

all: eht_keygen eht_siggen eht_sigparse eht_print_sk eht_print_pk eht_hash eht_verify

eht_keygen: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) keygen.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) keygen.c

eht_siggen: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) siggen.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) siggen.c

eht_sigparse: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) sigparse.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) sigparse.c

eht_print_sk: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) print_sk.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) print_sk.c

eht_print_pk: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) print_pk.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) print_pk.c

eht_hash: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) hash.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) hash.c

eht_verify: $(REF_HEADERS) $(REF_SOURCES) $(HEADERS) $(SOURCES) verify.c
	$(CC) $(CFLAGS) -o $@ $(REF_SOURCES) $(SOURCES) $(LDFLAGS) verify.c

.PHONY: clean run

clean:
	-rm eht_keygen eht_siggen eht_sigpars eht_print_sk eht_print_pk eht_hash eht_verify

run: eht_keygen eht_siggen
	./eht_keygen 0
	./eht_siggen private.sk 2 0 > sigs
	./eht_sigparse public.pk < sigs
