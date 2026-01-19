"""
API Tests for BA Project
Tests health check endpoints and basic API functionality
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_endpoint(self, client):
        """Test /health returns 200 and healthy status"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data

    def test_ready_endpoint(self, client):
        """Test /ready returns status and checks"""
        response = client.get('/ready')
        # Should return 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert 'status' in data
        assert 'checks' in data

    def test_metrics_endpoint(self, client):
        """Test /metrics returns Prometheus-compatible metrics"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')
        # Check for expected metric names
        content = response.data.decode('utf-8')
        assert 'app_info' in content
        assert 'logger_queue_size' in content


class TestMainRoutes:
    """Test main application routes"""

    def test_index_page(self, client):
        """Test index page loads"""
        response = client.get('/')
        assert response.status_code == 200

    def test_login_creates_session(self, client):
        """Test login endpoint creates session"""
        response = client.post('/login', json={'user_id': 'test_user_123'})
        # Should redirect or return success
        assert response.status_code in [200, 302]


class TestRecommender:
    """Test recommender functionality"""

    def test_recommender_module_imports(self):
        """Test that recommender module can be imported"""
        from utils.recommender import get_recommendations, MovieDataset
        assert callable(get_recommendations)
        assert MovieDataset is not None

    def test_get_recommendations_control(self):
        """Test control variant recommendations"""
        from utils.recommender import get_recommendations
        recs = get_recommendations('test_user', 'control', n=5)
        assert isinstance(recs, list)
        assert len(recs) <= 5
        if recs:
            assert 'movieId' in recs[0]
            assert 'title' in recs[0]

    def test_get_recommendations_treatment(self):
        """Test treatment variant recommendations"""
        from utils.recommender import get_recommendations
        recs = get_recommendations('test_user', 'treatment', n=5)
        assert isinstance(recs, list)
        assert len(recs) <= 5


class TestConfig:
    """Test configuration"""

    def test_config_loads(self):
        """Test configuration can be loaded"""
        from config import get_config, Config
        config = get_config()
        assert config is not None
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'MONGODB_URI')

    def test_environment_config(self):
        """Test environment-based configuration"""
        from config import config
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config


class TestLoggerService:
    """Test logger service"""

    def test_logger_service_imports(self):
        """Test logger service can be imported"""
        from utils.logger_service import (
            log_impression_async,
            log_click_async,
            log_conversion_async,
            get_queue_size
        )
        assert callable(log_impression_async)
        assert callable(log_click_async)
        assert callable(log_conversion_async)
        assert callable(get_queue_size)

    def test_log_event_returns_true(self):
        """Test logging returns True on success"""
        from utils.logger_service import log_impression_async
        result = log_impression_async('test_user', 'control', [1, 2, 3])
        assert result is True

    def test_queue_size_is_integer(self):
        """Test queue size returns integer"""
        from utils.logger_service import get_queue_size
        size = get_queue_size()
        assert isinstance(size, int)
        assert size >= 0


class TestMetrics:
    """Test metrics calculation"""

    def test_metrics_module_imports(self):
        """Test metrics module can be imported"""
        from utils.metrics import calculate_metrics, check_srm, calculate_lift
        assert callable(calculate_metrics)
        assert callable(check_srm)
        assert callable(calculate_lift)

    def test_calculate_metrics_returns_dict(self):
        """Test calculate_metrics returns expected structure"""
        from utils.metrics import calculate_metrics
        metrics = calculate_metrics()
        assert isinstance(metrics, dict)
        assert 'control' in metrics
        assert 'treatment' in metrics
        assert 'impressions' in metrics['control']
        assert 'clicks' in metrics['control']

    def test_check_srm(self):
        """Test SRM check function"""
        from utils.metrics import check_srm
        metrics = {
            'control': {'users': 100},
            'treatment': {'users': 100}
        }
        result = check_srm(metrics)
        assert 'has_srm' in result
        assert 'message' in result
        assert result['has_srm'] is False  # 50/50 split should not have SRM
