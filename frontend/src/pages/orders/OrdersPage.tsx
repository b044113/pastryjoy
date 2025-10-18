import React, { useState, useEffect } from 'react';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loading } from '../../components/common/Loading';
import { orderService } from '../../services/order.service';
import { productService } from '../../services/product.service';
import { useAuth } from '../../contexts/AuthContext';
import type { Order, Product } from '../../types';

export const OrdersPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    notes: '',
    items: [] as { product_id: string; quantity: number; unit_price: number }[],
  });
  const [statusUpdate, setStatusUpdate] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // For adding items to order
  const [selectedProductId, setSelectedProductId] = useState('');
  const [itemQuantity, setItemQuantity] = useState('1');
  const [itemPrice, setItemPrice] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [ordersData, productsData] = await Promise.all([
        orderService.getAll(),
        productService.getAll(),
      ]);
      setOrders(ordersData);
      setProducts(productsData);
    } catch (err: any) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = () => {
    setFormData({
      customer_name: '',
      customer_email: '',
      notes: '',
      items: [],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({
      customer_name: '',
      customer_email: '',
      notes: '',
      items: [],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
  };

  const handleOpenStatusModal = (order: Order) => {
    setSelectedOrder(order);
    setStatusUpdate(order.status);
    setIsStatusModalOpen(true);
  };

  const handleCloseStatusModal = () => {
    setIsStatusModalOpen(false);
    setSelectedOrder(null);
    setStatusUpdate('');
  };

  const handleAddItem = () => {
    if (!selectedProductId || !itemQuantity || !itemPrice) {
      setError('Please select a product, enter quantity and price');
      return;
    }

    const quantity = parseFloat(itemQuantity);
    const price = parseFloat(itemPrice);

    if (quantity <= 0 || price < 0) {
      setError('Quantity must be greater than 0 and price must be non-negative');
      return;
    }

    // Check if product already added
    if (formData.items.some((item) => item.product_id === selectedProductId)) {
      setError('Product already added');
      return;
    }

    setFormData({
      ...formData,
      items: [
        ...formData.items,
        { product_id: selectedProductId, quantity, unit_price: price },
      ],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
  };

  const handleRemoveItem = (productId: string) => {
    setFormData({
      ...formData,
      items: formData.items.filter((item) => item.product_id !== productId),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.items.length === 0) {
      setError('Please add at least one item');
      return;
    }

    setSubmitting(true);

    try {
      await orderService.create({
        customer_name: formData.customer_name,
        customer_email: formData.customer_email,
        notes: formData.notes || undefined,
        items: formData.items,
      });
      await loadData();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create order');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedOrder) return;

    setSubmitting(true);
    try {
      await orderService.updateStatus(selectedOrder.id, {
        status: statusUpdate as any,
      });
      await loadData();
      handleCloseStatusModal();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this order?')) return;

    try {
      await orderService.delete(id);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete order');
    }
  };

  const getProductName = (productId: string): string => {
    const product = products.find((prod) => prod.id === productId);
    return product?.name || 'Unknown';
  };

  const getStatusBadgeColor = (status: string): string => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-purple-100 text-purple-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const calculateOrderTotal = (): number => {
    return formData.items.reduce(
      (sum, item) => sum + item.quantity * item.unit_price,
      0
    );
  };

  if (loading) return <Loading fullScreen />;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
            <p className="text-gray-600 mt-2">
              {isAdmin() ? 'Manage all orders' : 'View and create your orders'}
            </p>
          </div>
          <Button onClick={handleOpenModal}>+ Create Order</Button>
        </div>

        {orders.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No orders yet
              </h3>
              <p className="text-gray-600 mb-6">
                Get started by creating your first order
              </p>
              <Button onClick={handleOpenModal}>Create First Order</Button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <Card key={order.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {order.customer_name}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(
                          order.status
                        )}`}
                      >
                        {order.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{order.customer_email}</p>
                    {order.notes && (
                      <p className="text-sm text-gray-500 mt-1 italic">
                        Note: {order.notes}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">
                      ${order.total.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Order Items */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Items ({order.items.length}):
                  </p>
                  <div className="space-y-1">
                    {order.items.map((item) => (
                      <div
                        key={item.id}
                        className="flex justify-between text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded"
                      >
                        <span>
                          {item.product_name || 'Product'} × {item.quantity}
                        </span>
                        <span className="font-medium">
                          ${item.total.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {isAdmin() && (
                    <>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenStatusModal(order)}
                      >
                        Update Status
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(order.id)}
                      >
                        Delete
                      </Button>
                    </>
                  )}
                  {!isAdmin() && order.status === 'pending' && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(order.id)}
                    >
                      Cancel Order
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Create Order Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title="Create Order"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Order'}
              </Button>
            </>
          }
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Customer Name"
              value={formData.customer_name}
              onChange={(e) =>
                setFormData({ ...formData, customer_name: e.target.value })
              }
              required
              disabled={submitting}
            />

            <Input
              label="Customer Email"
              type="email"
              value={formData.customer_email}
              onChange={(e) =>
                setFormData({ ...formData, customer_email: e.target.value })
              }
              required
              disabled={submitting}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
                disabled={submitting}
              />
            </div>

            {/* Add Items Section */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">
                Order Items
              </h4>

              <div className="flex gap-2 mb-3">
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={submitting}
                >
                  <option value="">Select product...</option>
                  {products.map((prod) => (
                    <option key={prod.id} value={prod.id}>
                      {prod.name}
                    </option>
                  ))}
                </select>

                <Input
                  type="number"
                  step="0.001"
                  placeholder="Qty"
                  value={itemQuantity}
                  onChange={(e) => setItemQuantity(e.target.value)}
                  disabled={submitting}
                  className="w-24"
                />

                <Input
                  type="number"
                  step="0.01"
                  placeholder="Price"
                  value={itemPrice}
                  onChange={(e) => setItemPrice(e.target.value)}
                  disabled={submitting}
                  className="w-24"
                />

                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddItem}
                  disabled={submitting}
                >
                  Add
                </Button>
              </div>

              {/* List of added items */}
              {formData.items.length > 0 && (
                <div className="space-y-2">
                  {formData.items.map((item) => (
                    <div
                      key={item.product_id}
                      className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg"
                    >
                      <span className="text-sm">
                        {getProductName(item.product_id)} - {item.quantity} ×{' '}
                        ${item.unit_price.toFixed(2)} = $
                        {(item.quantity * item.unit_price).toFixed(2)}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(item.product_id)}
                        className="text-red-600 hover:text-red-700 text-sm"
                        disabled={submitting}
                      >
                        Remove
                      </button>
                    </div>
                  ))}

                  <div className="flex justify-between items-center pt-2 border-t">
                    <span className="font-medium text-gray-900">Total:</span>
                    <span className="text-xl font-bold text-primary-600">
                      ${calculateOrderTotal().toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              {formData.items.length === 0 && (
                <p className="text-sm text-gray-500 italic">
                  No items added yet
                </p>
              )}
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
          </form>
        </Modal>

        {/* Update Status Modal */}
        <Modal
          isOpen={isStatusModalOpen}
          onClose={handleCloseStatusModal}
          title="Update Order Status"
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseStatusModal}>
                Cancel
              </Button>
              <Button onClick={handleUpdateStatus} disabled={submitting}>
                {submitting ? 'Updating...' : 'Update'}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Order: {selectedOrder?.customer_name}
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={statusUpdate}
                onChange={(e) => setStatusUpdate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={submitting}
              >
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};
