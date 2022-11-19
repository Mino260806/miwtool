from component import Component


class WatchFace:
    def __init__(self):
        self.components = []
        self.preview = None
        self.name = None
        self.face_id = None

    def show_all(self):
        self.preview.show()
        for component in self.components:
            component.show()

    def dump(self, path):
        return {
            "name": self.name,
            "id": self.face_id,
            "preview": self.preview.dump(path, "preview"),
            "components": self.dump_components(path)
        }

    def dump_components(self, path):
        dump = []
        for i, component in enumerate(self.components):
            dump.append(component.dump(path, str(i)))
        return dump

    def load_from_dump(self, path, dump):
        self.name = dump["name"]
        self.face_id = dump["id"]
        self.preview = Component(Component.PREVIEW)
        self.preview.load_from_dump(path, dump.get("preview"))
        components = dump.get("components")
        if components:
            for component in components:
                self.components.append(Component(Component.WIDGET))
                self.components[-1].load_from_dump(path, component)

