import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import historyService from '../services/historyService';
import { HistoryItem } from '../types/history';
import { 
  History, 
  Heart, 
  Wind, 
  Filter, 
  FileText, 
  ChevronLeft, 
  ChevronRight, 
  Clock,
  Layers,
  ArrowUpDown,
  AlertCircle,
  RotateCcw
} from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(10);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [classFilter, setClassFilter] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await historyService.getHistory({
        skip: page * limit,
        limit,
        category: categoryFilter || undefined,
        classification: classFilter || undefined,
      });

      // Sort items locally if order changed
      let fetchedItems = res.items;
      if (sortOrder === 'asc') {
        fetchedItems = [...fetchedItems].reverse();
      }
      setItems(fetchedItems);
      setTotal(res.total);
    } catch (err: any) {
      console.error('Failed to fetch history:', err);
      setError(err.response?.data?.detail || 'Failed to load screening history. Please check connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, categoryFilter, classFilter, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder((prev) => (prev === 'desc' ? 'asc' : 'desc'));
  };

  const handleRowClick = (item: HistoryItem) => {
    if (item.analysis_id) {
      navigate(`/report/${item.analysis_id}`);
    }
  };

  const resetFilters = () => {
    setCategoryFilter('');
    setClassFilter('');
    setSortOrder('desc');
    setPage(0);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2.5">
            <History className="w-7 h-7 text-cyan-400" />
            Screening History
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Archived digital stethoscope recordings and AI diagnostic findings ({total} records).
          </p>
        </div>

        {/* Filter & Sort Controls */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Category Filter */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(0);
              }}
              className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none"
            >
              <option value="">All Categories</option>
              <option value="heart">Heart Sounds</option>
              <option value="lung">Lung Sounds</option>
              <option value="mixed">Mixed Sounds</option>
            </select>
          </div>

          {/* Result / Classification Filter */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
            <select
              value={classFilter}
              onChange={(e) => {
                setClassFilter(e.target.value);
                setPage(0);
              }}
              className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none"
            >
              <option value="">All Results</option>
              <option value="Normal">Normal Only</option>
              <option value="Abnormal">Abnormal Only</option>
            </select>
          </div>

          {/* Sort By Date */}
          <button
            type="button"
            onClick={toggleSortOrder}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
            title="Toggle sort order"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-cyan-400" />
            <span>Date: {sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
          </button>

        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-between gap-3 text-rose-400 text-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchHistory}
            className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 rounded-lg text-xs font-bold transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* History Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center text-slate-500 gap-3">
            <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
            <span className="text-xs">Loading screening records...</span>
          </div>
        ) : items.length === 0 ? (
          <div className="py-16 text-center space-y-3">
            <History className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-300">No matching recordings found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try resetting your search filters or record a new digital stethoscope audio session.
            </p>
            {(categoryFilter || classFilter) && (
              <button
                type="button"
                onClick={resetFilters}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-slate-800 text-cyan-400 hover:bg-slate-700 text-xs font-bold transition-colors mt-2"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reset Filters
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Recording & Date</th>
                  <th className="px-6 py-4">Category & Site</th>
                  <th className="px-6 py-4">AI Diagnosis</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Report Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {items.map((item) => (
                  <tr
                    key={item.recording_id}
                    onClick={() => handleRowClick(item)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    
                    {/* Recording & Date */}
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">
                        {item.file_name}
                      </div>
                      <div className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {new Date(item.date).toLocaleString()}
                      </div>
                    </td>

                    {/* Category & Site */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {item.category === 'heart' ? (
                          <Heart className="w-4 h-4 text-rose-400 shrink-0" />
                        ) : (
                          <Wind className="w-4 h-4 text-cyan-400 shrink-0" />
                        )}
                        <span className="font-semibold text-xs uppercase tracking-wider text-slate-300">
                          {item.category}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Site: <strong>{item.chest_location}</strong> ({item.duration_seconds.toFixed(1)}s)
                      </div>
                    </td>

                    {/* AI Diagnosis */}
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-100">{item.prediction}</div>
                      {item.confidence && (
                        <div className="text-xs text-cyan-400 mt-0.5 font-medium">
                          Confidence: {(item.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </td>

                    {/* Result Status Badge */}
                    <td className="px-6 py-4">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                          item.classification === 'Normal'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {item.classification}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        {item.analysis_id && (
                          <Link
                            to={`/report/${item.analysis_id}`}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 transition-colors"
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>View Report</span>
                          </Link>
                        )}
                        {item.analysis_id && (
                          <Link
                            to={`/analysis/${item.analysis_id}`}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                            title="View Raw Spectrogram & Saliency"
                          >
                            <Layers className="w-4 h-4" />
                          </Link>
                        )}
                      </div>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="px-6 py-4 bg-slate-950/60 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Showing Page {page + 1} of {totalPages} ({total} recordings)
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
