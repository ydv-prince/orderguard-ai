/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Shield, Search, X, Plus, CreditCard, ChevronRight } from 'lucide-react';
import api from '../api';

interface Prediction {
  risk_score: number;
  risk_tier: string;
  reasons: Record<string, unknown>;
}

interface Order {
  id: string;
  customer_details: Record<string, unknown>;
  total_amount: number;
  status: string;
  predictions: Prediction[];
  created_at: string;
}

export default function Dashboard() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewOrder, setReviewOrder] = useState<Order | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [newOrderForm, setNewOrderForm] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    amount: '',
    itemsCount: '1'
  });
  const [formError, setFormError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders/');
      // Sort by newest first
      const sorted = response.data.sort((a: Order, b: Order) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setOrders(sorted);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const getRiskColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!newOrderForm.name || !newOrderForm.email || !newOrderForm.amount || !newOrderForm.address) {
      setFormError('Please fill out all required fields.');
      return;
    }

    const amt = parseFloat(newOrderForm.amount);
    if (isNaN(amt) || amt < 0) {
      setFormError('Please enter a valid, non-negative amount.');
      return;
    }

    try {
      setActionLoading(true);
      const newOrder = {
        customer_details: {
          name: newOrderForm.name,
          email: newOrderForm.email,
          phone: newOrderForm.phone
        },
        shipping_address: newOrderForm.address,
        items: Array.from({ length: parseInt(newOrderForm.itemsCount) || 1 }).map(() => ({
          item_id: `SKU-${Math.floor(Math.random() * 1000)}`,
          price: amt / (parseInt(newOrderForm.itemsCount) || 1)
        })),
        total_amount: amt
      };
      await api.post('/orders/', newOrder);
      await fetchOrders();
      setShowOrderForm(false);
      setNewOrderForm({ name: '', email: '', phone: '', address: '', amount: '', itemsCount: '1' });
    } catch (error) {
      console.error('Failed to simulate order:', error);
      setFormError('API error occurred while creating order. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleVerify = async (action: 'approve' | 'prepaid_only' | 'investigate') => {
    if (!reviewOrder) return;
    try {
      setActionLoading(true);
      await api.post(`/orders/${reviewOrder.id}/verify`, {
        action,
        notes: reviewNotes
      });
      setReviewOrder(null);
      setReviewNotes('');
      await fetchOrders();
    } catch (error) {
      console.error('Verification failed:', error);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-8 max-w-7xl mx-auto font-sans"
    >
      <header className="mb-10 flex justify-between items-end border-b border-gray-200 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Shield className="w-6 h-6 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Verification Queue</h1>
          </div>
          <p className="text-gray-500 text-sm">Monitor and secure incoming COD orders</p>
        </div>
        <button
          onClick={() => setShowOrderForm(true)}
          disabled={actionLoading}
          className="cursor-pointer flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-5 py-2.5 rounded-lg shadow-sm hover:shadow-md hover:-translate-y-[1px] font-medium transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
        >
          <Plus className="w-4 h-4" />
          Simulate New Order
        </button>
      </header>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden"
        >
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Assessment</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                        <Search className="w-8 h-8 text-gray-400" />
                      </div>
                      <p className="text-gray-900 font-medium text-lg">No orders found</p>
                      <p className="text-gray-500 mt-1 max-w-sm mx-auto">Click "Simulate New Order" to generate test data and populate your verification queue.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                orders.map((order) => {
                  const latestPrediction = order.predictions?.length > 0 ? order.predictions[0] : null;
                  return (
                    <tr key={order.id} className="hover:bg-gray-50/80 transition-all duration-200 hover:-translate-y-[1px] hover:shadow-[0_2px_8px_rgba(0,0,0,0.04)] relative z-0 hover:z-10 bg-white">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(order.customer_details?.name as string) || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹{order.total_amount.toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${order.status === 'pending' ? 'bg-blue-100 text-blue-800' :
                            order.status === 'verified' ? 'bg-green-100 text-green-800' :
                              order.status === 'prepaid_required' ? 'bg-purple-100 text-purple-800' :
                                'bg-red-100 text-red-800'}`}>
                          {order.status === 'prepaid_required' ? 'PREPAID REQUIRED' : order.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {latestPrediction ? (
                          <div className="flex flex-col gap-1">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full w-max ${getRiskColor(latestPrediction.risk_tier)}`}>
                              {latestPrediction.risk_tier.toUpperCase()} ({(latestPrediction.risk_score * 100).toFixed(1)}%)
                            </span>
                          </div>
                        ) : (
                          <span className="text-gray-400 text-xs">Evaluating...</span>
                        )}
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap text-sm text-gray-500">
                        {order.status === 'pending' ? (
                          <button
                            onClick={() => setReviewOrder(order)}
                            className="cursor-pointer flex items-center gap-1 text-primary-600 hover:text-primary-800 font-medium group"
                          >
                            Review <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                          </button>
                        ) : (
                          <span className="text-gray-400 flex items-center gap-1.5"><CheckCircle className="w-4 h-4" /> Processed</span>
                        )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </motion.div>
      )}

      <AnimatePresence>
        {/* Create Order Modal */}
        {showOrderForm && (
          <div className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl max-w-md w-full p-7 shadow-2xl"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <Plus className="w-5 h-5 text-primary-600" /> Simulate New Order
                </h3>
                <button onClick={() => setShowOrderForm(false)} className="cursor-pointer text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"><X className="w-5 h-5" /></button>
              </div>

              {formError && (
                <div className="mb-4 bg-red-50 text-red-700 p-3 rounded text-sm">
                  {formError}
                </div>
              )}

              <form onSubmit={handleCreateOrder} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name *</label>
                  <input
                    type="text" required
                    className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                    value={newOrderForm.name}
                    onChange={(e) => setNewOrderForm({ ...newOrderForm, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                  <input
                    type="email" required
                    className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                    value={newOrderForm.email}
                    onChange={(e) => setNewOrderForm({ ...newOrderForm, email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                    value={newOrderForm.phone}
                    onChange={(e) => setNewOrderForm({ ...newOrderForm, phone: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Shipping Address *</label>
                  <input
                    type="text" required
                    className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                    value={newOrderForm.address}
                    onChange={(e) => setNewOrderForm({ ...newOrderForm, address: e.target.value })}
                  />
                </div>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Amount (INR) *</label>
                    <input
                      type="number" required min="0" step="0.01"
                      className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                      value={newOrderForm.amount}
                      onChange={(e) => setNewOrderForm({ ...newOrderForm, amount: e.target.value })}
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Items Count</label>
                    <input
                      type="number" min="1"
                      className="w-full border border-gray-300 rounded-lg p-2.5 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none"
                      value={newOrderForm.itemsCount}
                      onChange={(e) => setNewOrderForm({ ...newOrderForm, itemsCount: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowOrderForm(false)}
                    disabled={actionLoading}
                    className="cursor-pointer px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium transition-all active:scale-95 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={actionLoading}
                    className="cursor-pointer px-5 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 shadow-sm hover:shadow text-sm font-medium transition-all active:scale-95 disabled:opacity-50"
                  >
                    {actionLoading ? 'Creating...' : 'Create Order'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* Review Modal */}
        {reviewOrder && (
          <div className="fixed inset-0 bg-gray-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl max-w-lg w-full p-7 shadow-2xl"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900">Review Order {reviewOrder.id}</h3>
                <button onClick={() => setReviewOrder(null)} className="cursor-pointer text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"><X className="w-5 h-5" /></button>
              </div>

              <div className="mb-6 bg-gray-50/50 p-5 rounded-xl border border-gray-100 hover:shadow-sm hover:border-gray-200 transition-all duration-300">
                <p className="text-sm text-gray-700"><strong>Customer:</strong> {String(reviewOrder.customer_details?.name)}</p>
                <p className="text-sm text-gray-700"><strong>Email:</strong> {String(reviewOrder.customer_details?.email)}</p>
                <p className="text-sm text-gray-700"><strong>Total Amount:</strong> ₹{reviewOrder.total_amount.toFixed(2)}</p>
                {reviewOrder.predictions?.[0] && (
                  <div className="mt-3 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300 group">
                    <p className="text-xs font-semibold uppercase text-gray-500 mb-2 group-hover:text-primary-600 transition-colors">AI Risk Assessment</p>
                    <p className="text-sm"><span className="font-medium">Score:</span> {(reviewOrder.predictions[0].risk_score * 100).toFixed(1)}%</p>
                    <p className="text-sm"><span className="font-medium">Risk Level:</span> <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full w-max ${getRiskColor(reviewOrder.predictions[0].risk_tier)}`}>{reviewOrder.predictions[0].risk_tier.toUpperCase()}</span></p>
                    <div className="mt-2">
                      <p className="text-sm font-medium">Contributing factors:</p>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {(reviewOrder.predictions[0].reasons?.top_features as string[])?.map((feature, idx) => (
                          <li key={idx}>{feature}</li>
                        ))}
                      </ul>
                      {Boolean(reviewOrder.predictions[0].reasons?.note) && (
                        <p className="text-xs text-gray-500 mt-2 italic">{reviewOrder.predictions[0].reasons.note as string}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Reviewer Notes (Optional)</label>
                <textarea
                  className="w-full border border-gray-300 rounded-lg p-3 text-sm hover:border-gray-400 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all outline-none resize-none"
                  rows={3}
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  placeholder="Add your investigation notes here..."
                ></textarea>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => handleVerify('prepaid_only')}
                  disabled={actionLoading}
                  className="cursor-pointer flex items-center gap-2 px-5 py-2.5 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm font-medium transition-all active:scale-95 disabled:opacity-50"
                >
                  <CreditCard className="w-4 h-4" /> Allow Prepaid Only
                </button>
                <button
                  onClick={() => handleVerify('approve')}
                  disabled={actionLoading}
                  className="cursor-pointer flex items-center gap-2 px-5 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium transition-all active:scale-95 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" /> Approve (Verify)
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
