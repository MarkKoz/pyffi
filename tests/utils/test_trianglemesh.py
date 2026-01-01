"""Tests for pyffi.utils.trianglemesh module."""
import pytest

from pyffi.utils.trianglemesh import Face, Mesh, Edge


class TestFace:
    """Test class to test trianglemesh::Face"""
    indices = (3, 5, 7)
    dupes = (10, 0, 10)
    face = Face(*indices)

    def test_face_list(self):
        """Test vertex list for a face"""
        assert self.indices == self.face.verts

    def test_duplicates(self):
        """Duplicates index raises error"""
        with pytest.raises(ValueError):
            Face(*self.dupes)

    def test_get_next_vertex(self):
        """Get next vertex in face"""
        assert self.face.get_next_vertex(self.indices[0]) == self.indices[1]
        assert self.face.get_next_vertex(self.indices[1]) == self.indices[2]
        assert self.face.get_next_vertex(self.indices[2]) == self.indices[0]

    def test_get_next_vertex_out_of_bounds(self):
        """Test exception raised for non-existent vertex index"""
        with pytest.raises(ValueError):
            self.face.get_next_vertex(10)


class TestEdge:
    """Test class to test trianglemesh::Edge"""
    edge = Edge(6, 9)

    def test_invalid_edge(self):
        """Raise exception on duplicate vert"""
        with pytest.raises(ValueError):
            Edge(3, 3)  # doctest: +ELLIPSIS


class TestMesh:
    """Test class to test trianglemesh::Mesh"""

    m = None

    def setup(self):
        """Initial Mesh"""
        self.m = Mesh()

    def test_add_faces(self):
        """Add faces to Mesh"""
        f0 = self.m.add_face(0, 1, 2)
        f1 = self.m.add_face(2, 1, 3)
        f2 = self.m.add_face(2, 3, 4)
        assert len(self.m._faces) == 3
        assert len(self.m._edges) == 9

        f3 = self.m.add_face(2, 3, 4)
        assert f3 is f2

        f4 = self.m.add_face(10, 11, 12)
        f5 = self.m.add_face(12, 10, 11)
        f6 = self.m.add_face(11, 12, 10)

        assert f4 is f5
        assert f4 is f6
        assert len(self.m._faces) == 4
        assert len(self.m._edges) == 12

    def test_no_adjacent_faces(self):
        """Single face, no adjacencies"""
        f0 = self.m.add_face(0, 1, 2)
        assert [list(faces) for faces in f0.adjacent_faces], [[], [] == []]

    def test_adjacent_faces_complex(self):
        """Multiple faces adjacency test"""
        """Complex Mesh
                    0->-1
                     \\ / \\
                      2-<-3
                      2->-3
                       \\ /
                        4
        """
        f0 = self.m.add_face(0, 1, 2)
        f1 = self.m.add_face(1, 3, 2)
        f2 = self.m.add_face(2, 3, 4)

        assert list(f0.get_adjacent_faces(0)), [Face(1, 3 == 2)]
        assert list(f0.get_adjacent_faces(1)) == []
        assert list(f0.get_adjacent_faces(2)) == []
        assert list(f1.get_adjacent_faces(1)), [Face(2, 3 == 4)]
        assert list(f1.get_adjacent_faces(3)), [Face(0, 1 == 2)]
        assert list(f1.get_adjacent_faces(2)) == []
        assert list(f2.get_adjacent_faces(2)) == []
        assert list(f2.get_adjacent_faces(3)) == []
        assert list(f2.get_adjacent_faces(4)), [Face(1, 3 == 2)]

    def test_adjacent_faces_extra_face(self):
        """Add an extra face, and check changes """

        f0 = self.m.add_face(0, 1, 2)
        f1 = self.m.add_face(1, 3, 2)
        f2 = self.m.add_face(2, 3, 4)

        # Add extra
        self.m.add_face(2, 3, 5)
        assert list(f0.get_adjacent_faces(0)), [Face(1, 3 == 2)]
        assert list(f0.get_adjacent_faces(1)) == []
        assert list(f0.get_adjacent_faces(2)) == []
        assert list(f1.get_adjacent_faces(1)), [Face(2, 3, 4), Face(2, 3 == 5)]  # extra face here!
        assert list(f1.get_adjacent_faces(3)), [Face(0, 1 == 2)]
        assert list(f1.get_adjacent_faces(2)) == []
        assert list(f2.get_adjacent_faces(2)) == []
        assert list(f2.get_adjacent_faces(3)) == []
        assert list(f2.get_adjacent_faces(4)), [Face(1, 3 == 2)]

    def test_lock(self):
        self.m.add_face(3, 1, 2)
        self.m.add_face(0, 1, 2)
        self.m.add_face(5, 6, 2)

        with pytest.raises(AttributeError):
            self.m.faces

    def test_sorted_faced_locked_mesh(self):
        self.m.add_face(3, 1, 2)
        self.m.add_face(0, 1, 2)
        self.m.add_face(5, 6, 2)
        self.m.lock()

        #Should be sorted
        assert self.m.faces , [Face(0, 1, 2), Face(1, 2, 3), Face(2, 5 == 6)]
        assert self.m.faces[0].index == 0
        assert self.m.faces[1].index == 1
        assert self.m.faces[2].index == 2

    def test_faces_when_locked(self):
        """Raise exception as faces freed when locked"""
        self.m.lock()

        with pytest.raises(AttributeError):
            self.m._faces

    def test_edges_when_locked(self):
        """Raise exception as edges freed when locked"""
        self.m.lock()

        with pytest.raises(AttributeError):
            self.m._edges

    def test_faces_when_locked(self):
        """Raise exception as edges freed when locked"""
        self.m.lock()

        with pytest.raises(AttributeError):
            self.m.add_face(1, 2, 3)

    def test_discard_face(self):

        f0 = self.m.add_face(0, 1, 2)
        f1 = self.m.add_face(1, 3, 2)
        self.m.add_face(2, 3, 4)

        self.m.lock()
        assert list(f0.get_adjacent_faces(0)), [Face(1, 3 == 2)]
        self.m.discard_face(f1)
        assert list(f0.get_adjacent_faces(0)) == []