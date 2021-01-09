from typing import List

from src.GraphAlgoInterface import GraphAlgoInterface
from src.GraphInterface import GraphInterface
from src.DiGraph import DiGraph
from src.utilities.Heap import Heap
from src.NodeData import NodeData
from src.SCCAlgo import SCCAlgo
from src.utilities import Jsonconverter as JGraph


class _DistNode(NodeData):
    def __init__(self):
        self.path_parent: _DistNode = None
        self.path_distance: float = -1

    def add_fields(self, parent: __init__, distance: float):
        self.path_parent: _DistNode = parent
        self.path_distance = distance

    def remove_fields(self):
        delattr(self, "path_parent")
        delattr(self, "path_distance")

    def is_dist_node(self):
        return hasattr(self, "path_parent")


class GraphAlgo(GraphAlgoInterface):
    """
    this class get a graph and create graph algo from it, if the graph is not of the right format
    convert it to be DiGraph algo.
    """

    def __init__(self, graph: DiGraph = None):
        self._graph: DiGraph = None
        self._scc = SCCAlgo()
        self._scc_update = -1
        self.set_graph(graph)

    def set_graph(self, graph):
        if graph is None:
            graph = DiGraph()
        elif not isinstance(graph, DiGraph):
            graph = DiGraph(graph)
        self._graph = graph
        self._scc_update = -1

    def get_graph(self) -> DiGraph:
        return self._graph

    # noinspection PyTypeChecker
    def shortest_path(self, id1: int, id2: int) -> (float, list):
        start: _DistNode = self._graph.get_node(id1)
        dest: _DistNode = self._graph.get_node(id2)

        if dest is None or start is None:
            return float("inf"), []

        if dest == start:
            return 0, [dest.get_key(), start.get_key()]

        modified = [start]
        path = []

        shortest_dist = float("inf")
        heap = Heap()
        _DistNode.add_fields(start, None, 0)
        heap.add_item(start, 0)
        while heap.size() > 0:
            current: _DistNode = heap.pop_first()[0]
            if current == dest:
                shortest_dist = current.path_distance
                while current is not None:
                    path.insert(0, current.get_key())
                    current = current.path_parent
                break

            edge: (int, float)
            for edge in self._graph.all_out_edges_of_node(current.get_key()).items():
                neighbour: _DistNode = self._graph.get_node(edge[0])
                distance = current.path_distance + edge[1]
                if _DistNode.is_dist_node(neighbour):
                    if neighbour.path_distance > distance:
                        neighbour.path_distance = distance
                        neighbour.path_parent = current
                        heap.heapify_up(neighbour, distance)
                else:
                    _DistNode.add_fields(neighbour, current, distance)
                    heap.add_item(neighbour, distance)
                    modified.append(neighbour)
        heap.__del__()
        for node in modified:
            _DistNode.remove_fields(node)
        return shortest_dist, path

    """
    Returns the shortest path from node id1 to node id2 using Dijkstra's Algorithm
    @param id1: The start node id
    @param id2: The end node id
    @return: (path_distance, path) : (float, list)
    """

    def connected_component(self, id1: int) -> list:
        node: NodeData = self._graph.get_node(id1)
        if node is None:
            return []
        scc: list
        for scc in self.connected_components():
            if scc.__contains__(id1):
                return scc
        return []

    def connected_components(self) -> List[list]:
        if self._scc_update == self._graph.get_mc():
            return self._scc.components
        self._scc.calculate_scc(self._graph)
        self._scc_update = self._graph.get_mc()
        return self._scc.components

    def plot_graph(self) -> None:
        pass

    def save_to_json(self, file_name: str) -> bool:
        try:
            JGraph.save_graph(self._graph, file_name)
            return True
        except:
            return False

    def load_from_json(self, file_name: str) -> bool:
        try:
            graph = JGraph.load_graph(file_name)
            if graph is None:
                return False
            self._graph = graph
            return True
        except:
            return False
