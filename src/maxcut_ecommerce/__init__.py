"""Max-Cut aplicado a relações de produtos de ecommerce."""

from .baseline import brute_force_max_cut
from .instance import EcommerceInstance, load_instance

__all__ = ["EcommerceInstance", "load_instance", "brute_force_max_cut"]
