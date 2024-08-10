APP_NAME := translator
SRC := translator.go

# Platforms for cross-compilation
PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64

# LDFLAGS for optimizations
LDFLAGS := -s -w


.PHONY: tidy
tidy:
	@echo "Tidying up Go module..."
	go mod tidy


.PHONY: all
all: build


.PHONY: build
build:
	@echo "Building $(APP_NAME)..."
	@mkdir ./bin
	go build -ldflags="$(LDFLAGS)" -o $(APP_NAME) $(SRC)


.PHONY: static
static:
	@echo "Building static binary..."
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -ldflags="$(LDFLAGS)" -o $(APP_NAME)-static $(SRC)


.PHONY: cross-compile
cross-compile:
	@echo "Cross-compiling for multiple platforms..."
	@mkdir ./bin
	@for platform in $(PLATFORMS); do \
		GOOS=$$(echo $$platform | cut -d'/' -f1) ; \
		GOARCH=$$(echo $$platform | cut -d'/' -f2) ; \
		OUTPUT=$(APP_NAME)-$$GOOS-$$GOARCH ; \
		echo "Building $$OUTPUT..." ; \
		CGO_ENABLED=0 GOOS=$$GOOS GOARCH=$$GOARCH go build -a -installsuffix cgo -ldflags="$(LDFLAGS)" -o ./bin/$$OUTPUT $(SRC) ; \
	done


.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -f $(APP_NAME) ./bin/$(APP_NAME)__*
