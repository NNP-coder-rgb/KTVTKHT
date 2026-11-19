// State toàn cục của ứng dụng
const AppState = {
  currentUser: null,
  allUsers: [],
  categories: [],
  feedbacks: [],
  currentTab: 'submit',
  liveAiTimer: null
};

// Khởi chạy khi load trang
document.addEventListener('DOMContentLoaded', async () => {
  await loadUsers();
  await loadCategories();
  setupNavigation();
  setupLiveAiPreview();
  setupFormSubmissions();
  
  // Khởi tạo tab mặc định
  switchTab('submit');
});

// ====================================================================
// 1. Quản lý Người dùng & Chuyển đổi vai trò (User Switcher)
// ====================================================================
async function loadUsers() {
  try {
    const res = await fetch('/api/users');
    AppState.allUsers = await res.json();
    
    const selector = document.getElementById('user-selector');
    selector.innerHTML = '';
    
    // Tìm kiếm trong localStorage hoặc lấy mặc định
    const savedUserId = localStorage.getItem('edu_feedback_user_id');
    
    AppState.allUsers.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.id;
      const roleIcon = u.role === 'ADMIN' ? '🛡️ [BQL/Admin]' : (u.role === 'TEACHER' ? '👨‍🏫 [Giảng viên]' : '🎓 [Sinh viên]');
      opt.textContent = `${roleIcon} ${u.name} (${u.detail || u.email})`;
      selector.appendChild(opt);
    });

    if (savedUserId && AppState.allUsers.some(u => u.id == savedUserId)) {
      selector.value = savedUserId;
    } else {
      // Mặc định chọn Sinh viên Hà Minh Diệu (Nhóm trưởng)
      const dieu = AppState.allUsers.find(u => u.email === 'dieuhm@student.edu.vn') || AppState.allUsers[0];
      selector.value = dieu ? dieu.id : AppState.allUsers[0].id;
    }

    updateCurrentUserInfo();

    selector.addEventListener('change', (e) => {
      localStorage.setItem('edu_feedback_user_id', e.target.value);
      updateCurrentUserInfo();
      handleRoleChange();
    });

  } catch (err) {
    console.error('Lỗi khi tải danh sách users:', err);
  }
}

function updateCurrentUserInfo() {
  const selector = document.getElementById('user-selector');
  const userId = parseInt(selector.value);
  AppState.currentUser = AppState.allUsers.find(u => u.id === userId);
  
  const roleBadge = document.getElementById('current-user-role-badge');
  if (AppState.currentUser) {
    if (AppState.currentUser.role === 'ADMIN') {
      roleBadge.className = 'badge bg-danger ms-2';
      roleBadge.textContent = 'Quản trị viên / BQL';
    } else if (AppState.currentUser.role === 'TEACHER') {
      roleBadge.className = 'badge bg-success ms-2';
      roleBadge.textContent = 'Giảng viên';
    } else {
      roleBadge.className = 'badge bg-primary ms-2';
      roleBadge.textContent = 'Sinh viên';
    }
  }
}

function handleRoleChange() {
  // Cập nhật lại dữ liệu tab hiện tại khi đổi vai trò
  if (AppState.currentTab === 'my-feedbacks') {
    loadMyFeedbacks();
  } else if (AppState.currentTab === 'admin-inbox') {
    loadAdminFeedbacks();
  }
}

// ====================================================================
// 2. Quản lý Danh mục
// ====================================================================
async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    AppState.categories = await res.json();
    populateCategoryFilters();
  } catch (err) {
    console.error('Lỗi tải danh mục:', err);
  }
}

function populateCategoryFilters() {
  const filterSelect = document.getElementById('admin-filter-category');
  if (!filterSelect) return;
  
  filterSelect.innerHTML = '<option value="">-- Tất cả danh mục --</option>';
  AppState.categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.category_id;
    opt.textContent = `${cat.category_name} (${cat.category_code})`;
    filterSelect.appendChild(opt);
  });
}

// ====================================================================
// 3. Quản lý Điều hướng Tab
// ====================================================================
function setupNavigation() {
  const tabLinks = document.querySelectorAll('.nav-tabs-custom .nav-link');
  tabLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const tabId = link.getAttribute('data-tab');
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  AppState.currentTab = tabId;
  
  // Active nav link
  document.querySelectorAll('.nav-tabs-custom .nav-link').forEach(l => {
    l.classList.toggle('active', l.getAttribute('data-tab') === tabId);
  });

  // Show/Hide section
  document.querySelectorAll('.tab-section').forEach(sec => {
    sec.style.display = (sec.id === `tab-${tabId}`) ? 'block' : 'none';
  });

  // Tải dữ liệu tương ứng
  if (tabId === 'my-feedbacks') {
    loadMyFeedbacks();
  } else if (tabId === 'admin-inbox') {
    loadAdminFeedbacks();
  } else if (tabId === 'dashboard') {
    loadDashboardAnalytics();
  } else if (tabId === 'database-design') {
    loadDatabaseSchema();
  } else if (tabId === 'retrain-logs') {
    loadRetrainLogs();
  }
}

// ====================================================================
// 4. Live AI Preview (Phân tích tức thì khi sinh viên gõ văn bản)
// ====================================================================
function setupLiveAiPreview() {
  const titleInput = document.getElementById('input-feedback-title');
  const contentInput = document.getElementById('input-feedback-content');
  const previewBox = document.getElementById('live-ai-preview-box');

  const triggerAnalyze = () => {
    clearTimeout(AppState.liveAiTimer);
    const content = contentInput.value.trim();
    const title = titleInput.value.trim();

    if (!content) {
      previewBox.style.display = 'none';
      return;
    }

    AppState.liveAiTimer = setTimeout(async () => {
      try {
        const res = await fetch('/api/ai/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, content })
        });
        const data = await res.json();
        renderLiveAiPreview(data);
      } catch (err) {
        console.error('Lỗi phân tích AI tức thì:', err);
      }
    }, 350);
  };

  titleInput.addEventListener('input', triggerAnalyze);
  contentInput.addEventListener('input', triggerAnalyze);

  // Quick fill sample prompt buttons
  document.querySelectorAll('.btn-quick-sample').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const sampleText = btn.getAttribute('data-sample-content');
      const sampleTitle = btn.getAttribute('data-sample-title');
      titleInput.value = sampleTitle;
      contentInput.value = sampleText;
      triggerAnalyze();
    });
  });
}

function renderLiveAiPreview(data) {
  const previewBox = document.getElementById('live-ai-preview-box');
  if (!data.predicted_categories || data.predicted_categories.length === 0) {
    previewBox.style.display = 'none';
    return;
  }

  previewBox.style.display = 'block';

  // Sentiment badge
  let sentiHtml = '';
  const s = data.sentiment;
  if (s.label === 'POSITIVE') {
    sentiHtml = `<span class="badge-sentiment-pos"><i class="bi bi-emoji-smile"></i> Tích cực (${Math.round(s.score * 100)}%)</span>`;
  } else if (s.label === 'NEGATIVE') {
    sentiHtml = `<span class="badge-sentiment-neg"><i class="bi bi-emoji-frown"></i> Tiêu cực (${Math.round(s.score * 100)}%)</span>`;
  } else {
    sentiHtml = `<span class="badge-sentiment-neu"><i class="bi bi-emoji-neutral"></i> Trung tính</span>`;
  }

  if (s.is_urgent) {
    sentiHtml += ` <span class="badge-urgent"><i class="bi bi-exclamation-triangle-fill"></i> Ưu tiên khẩn cấp</span>`;
  }

  document.getElementById('live-ai-sentiment-badge').innerHTML = sentiHtml;

  // Categories Badges (Multi-label)
  const catContainer = document.getElementById('live-ai-categories-container');
  catContainer.innerHTML = '';

  data.predicted_categories.forEach(cat => {
    const badge = document.createElement('div');
    badge.className = 'd-flex align-items-center justify-content-between p-2 mb-2 rounded border bg-white';
    badge.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <span class="badge-category" style="background-color: ${cat.color};">
          <i class="bi ${cat.icon}"></i> ${cat.category_name}
        </span>
        <small class="text-muted">Từ khóa: <em>${cat.matched_keywords.join(', ')}</em></small>
      </div>
      <div class="text-end">
        <span class="badge bg-light text-dark border">Độ tin cậy: <strong>${Math.round(cat.confidence_score * 100)}%</strong></span>
      </div>
    `;
    catContainer.appendChild(badge);
  });

  // Clause evidence
  const evidenceBox = document.getElementById('live-ai-clause-evidence');
  if (data.clause_evidence && data.clause_evidence.length > 0) {
    evidenceBox.style.display = 'block';
    let evHtml = '<small class="text-muted d-block mb-1"><strong>Phân rã vế câu (Multi-label Explanation):</strong></small>';
    data.clause_evidence.forEach(item => {
      const catsMatched = Object.values(item.matches).map(m => `<span class="badge bg-secondary">${m.cat_name}</span>`).join(' ');
      evHtml += `<div class="p-1 mb-1 small text-dark bg-white border rounded">
        "<em>${item.clause}</em>" &rarr; ${catsMatched}
      </div>`;
    });
    evidenceBox.innerHTML = evHtml;
  } else {
    evidenceBox.style.display = 'none';
  }
}

// ====================================================================
// 5. Gửi Phản hồi mới (Student Submit)
// ====================================================================
function setupFormSubmissions() {
  const form = document.getElementById('form-submit-feedback');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!AppState.currentUser || AppState.currentUser.role !== 'STUDENT') {
      alert('Vui lòng chọn vai trò Sinh viên trên thanh chọn người dùng để gửi phản hồi!');
      return;
    }

    const title = document.getElementById('input-feedback-title').value.trim();
    const content = document.getElementById('input-feedback-content').value.trim();
    const isAnonymous = document.getElementById('input-feedback-anonymous').checked;
    const attachmentUrl = document.getElementById('input-feedback-attachment').value.trim() || null;

    if (!title || !content) {
      alert('Vui lòng nhập đầy đủ tiêu đề và nội dung phản hồi.');
      return;
    }

    const submitBtn = document.getElementById('btn-submit-feedback');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> AI đang phân loại & gửi...';

    try {
      const res = await fetch('/api/feedbacks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: AppState.currentUser.student_id,
          title,
          content,
          attachment_url: attachmentUrl,
          is_anonymous: isAnonymous
        })
      });

      const result = await res.json();
      if (res.ok) {
        alert('🎉 Gửi phản hồi thành công! Hệ thống AI đã tự động phân loại danh mục và cảm xúc.');
        form.reset();
        document.getElementById('live-ai-preview-box').style.display = 'none';
        switchTab('my-feedbacks');
      } else {
        alert('Lỗi: ' + (result.detail || 'Không thể gửi phản hồi'));
      }
    } catch (err) {
      console.error('Lỗi khi gửi phản hồi:', err);
      alert('Lỗi kết nối máy chủ!');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> Gửi Phản Hồi Ngay';
    }
  });
}

// ====================================================================
// 6. Hộp Thư Của Tôi (Student View)
// ====================================================================
async function loadMyFeedbacks() {
  const container = document.getElementById('my-feedbacks-container');
  container.innerHTML = '<div class="text-center py-4"><span class="spinner-border text-primary"></span> Đang tải...</div>';

  if (!AppState.currentUser || !AppState.currentUser.student_id) {
    container.innerHTML = `
      <div class="alert alert-warning">
        <i class="bi bi-info-circle me-2"></i> Bạn hiện đang chọn tài khoản <strong>${AppState.currentUser ? AppState.currentUser.name : 'Người dùng'}</strong> (không phải Sinh viên). 
        Hãy chuyển sang tài khoản Sinh viên ở góc trên bên phải để xem các phản hồi của bạn.
      </div>
    `;
    return;
  }

  try {
    const res = await fetch(`/api/feedbacks?student_id=${AppState.currentUser.student_id}`);
    const feedbacks = await res.json();

    if (feedbacks.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5 text-muted">
          <i class="bi bi-inbox fs-1 d-block mb-2"></i>
          <p>Bạn chưa gửi phản hồi nào. Hãy chuyển qua tab <strong>"Gửi Phản Hồi"</strong> để đóng góp ý kiến!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = '';
    feedbacks.forEach(fb => {
      container.appendChild(createFeedbackCard(fb, false));
    });
  } catch (err) {
    container.innerHTML = '<div class="alert alert-danger">Lỗi khi tải danh sách phản hồi.</div>';
  }
}

// ====================================================================
// 7. Bàn Làm Việc BQL (Admin Inbox & AI Moderation)
// ====================================================================
async function loadAdminFeedbacks() {
  const container = document.getElementById('admin-feedbacks-container');
  container.innerHTML = '<div class="text-center py-4"><span class="spinner-border text-primary"></span> Đang tải danh sách...</div>';

  const categoryId = document.getElementById('admin-filter-category').value;
  const status = document.getElementById('admin-filter-status').value;
  const sentiment = document.getElementById('admin-filter-sentiment').value;
  const isUrgent = document.getElementById('admin-filter-urgent').checked;
  const search = document.getElementById('admin-filter-search').value.trim();

  let url = '/api/feedbacks?';
  if (categoryId) url += `category_id=${categoryId}&`;
  if (status) url += `status=${status}&`;
  if (sentiment) url += `sentiment=${sentiment}&`;
  if (isUrgent) url += `is_urgent=true&`;
  if (search) url += `search=${encodeURIComponent(search)}&`;

  try {
    const res = await fetch(url);
    const feedbacks = await res.json();

    const countElem = document.getElementById('admin-feedback-count');
    if (countElem) countElem.textContent = feedbacks.length;

    if (feedbacks.length === 0) {
      container.innerHTML = '<div class="text-center py-5 text-muted"><i class="bi bi-check-circle fs-1 d-block mb-2 text-success"></i>Không tìm thấy phản hồi nào phù hợp với bộ lọc.</div>';
      return;
    }

    container.innerHTML = '';
    feedbacks.forEach(fb => {
      container.appendChild(createFeedbackCard(fb, true));
    });
  } catch (err) {
    container.innerHTML = '<div class="alert alert-danger">Lỗi khi tải phản hồi quản trị.</div>';
  }
}

// Filter listeners for Admin
document.getElementById('admin-filter-category').addEventListener('change', loadAdminFeedbacks);
document.getElementById('admin-filter-status').addEventListener('change', loadAdminFeedbacks);
document.getElementById('admin-filter-sentiment').addEventListener('change', loadAdminFeedbacks);
document.getElementById('admin-filter-urgent').addEventListener('change', loadAdminFeedbacks);
document.getElementById('admin-filter-search').addEventListener('input', () => {
  clearTimeout(AppState.searchTimer);
  AppState.searchTimer = setTimeout(loadAdminFeedbacks, 400);
});

// ====================================================================
// 8. Render Card Phản Hồi (Tái sử dụng cho Student và Admin)
// ====================================================================
function createFeedbackCard(fb, isAdminView) {
  const card = document.createElement('div');
  card.className = `feedback-item ${fb.is_urgent ? 'urgent-border' : ''}`;
  card.id = `fb-card-${fb.feedback_id}`;

  // Status badge
  let statusHtml = '';
  if (fb.status === 'PENDING') statusHtml = '<span class="status-pill status-pending"><i class="bi bi-clock-history"></i> Chờ tiếp nhận</span>';
  else if (fb.status === 'PROCESSING') statusHtml = '<span class="status-pill status-processing"><i class="bi bi-arrow-repeat"></i> Đang xử lý</span>';
  else if (fb.status === 'RESOLVED') statusHtml = '<span class="status-pill status-resolved"><i class="bi bi-check-circle"></i> Đã giải quyết</span>';
  else statusHtml = '<span class="status-pill status-rejected"><i class="bi bi-x-circle"></i> Từ chối</span>';

  // Sentiment badge
  let sentiHtml = '';
  if (fb.sentiment_label === 'POSITIVE') sentiHtml = '<span class="badge-sentiment-pos"><i class="bi bi-emoji-smile"></i> Tích cực</span>';
  else if (fb.sentiment_label === 'NEGATIVE') sentiHtml = '<span class="badge-sentiment-neg"><i class="bi bi-emoji-frown"></i> Tiêu cực</span>';
  else sentiHtml = '<span class="badge-sentiment-neu"><i class="bi bi-emoji-neutral"></i> Trung tính</span>';

  if (fb.is_urgent) {
    sentiHtml += ' <span class="badge-urgent ms-1"><i class="bi bi-exclamation-triangle-fill"></i> Khẩn cấp</span>';
  }

  // Categories Badges (Multi-label)
  let catsHtml = '';
  fb.categories.forEach(c => {
    catsHtml += `
      <span class="badge-category me-1 mb-1" style="background-color: ${c.color};">
        <i class="bi ${c.icon}"></i> ${c.category_name}
        ${isAdminView ? `<small class="opacity-75 ms-1">(${Math.round(c.confidence_score * 100)}%)</small>` : ''}
      </span>
    `;
  });

  // Anonymous / Student name
  const studentDisplay = fb.is_anonymous 
    ? '<span class="text-muted"><i class="bi bi-incognito"></i> Ẩn danh</span>' 
    : `<span class="fw-semibold text-primary"><i class="bi bi-person"></i> ${fb.student_name} (${fb.student_code} - ${fb.class_name})</span>`;

  // Responses list
  let responsesHtml = '';
  if (fb.responses && fb.responses.length > 0) {
    fb.responses.forEach(r => {
      responsesHtml += `
        <div class="response-thread">
          <div class="response-author">
            <i class="bi bi-reply-fill"></i> ${r.staff_name} &bull; <small class="text-muted fw-normal">${formatDate(r.created_at)}</small>
          </div>
          <div class="text-dark small">${escapeHtml(r.response_content)}</div>
        </div>
      `;
    });
  }

  // Admin action buttons
  let adminActionsHtml = '';
  if (isAdminView) {
    const isApproved = fb.is_reviewed && !fb.is_corrected_by_admin;
    const isCorrected = fb.is_corrected_by_admin;
    
    let reviewBadge = '';
    if (isApproved) {
      reviewBadge = '<span class="badge bg-success-subtle text-success border border-success-subtle me-2"><i class="bi bi-check2-all"></i> Đã duyệt AI</span>';
    } else if (isCorrected) {
      reviewBadge = '<span class="badge bg-warning-subtle text-warning border border-warning-subtle me-2"><i class="bi bi-pencil-square"></i> Đã chỉnh sửa nhãn</span>';
    } else {
      reviewBadge = '<span class="badge bg-secondary-subtle text-secondary border me-2"><i class="bi bi-robot"></i> Chờ duyệt AI</span>';
    }

    adminActionsHtml = `
      <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top flex-wrap gap-2">
        <div class="d-flex align-items-center">
          ${reviewBadge}
          <small class="text-muted">Phòng ban: <strong>${fb.assigned_department || 'Chưa phân'}</strong></small>
        </div>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-outline-success" onclick="quickApproveAI(${fb.feedback_id})">
            <i class="bi bi-check-lg"></i> Duyệt nhãn AI
          </button>
          <button class="btn btn-outline-warning" onclick="openOverrideModal(${fb.feedback_id})">
            <i class="bi bi-tags"></i> Sửa nhãn (Override)
          </button>
          <button class="btn btn-primary" onclick="openRespondModal(${fb.feedback_id}, '${escapeHtml(fb.title)}')">
            <i class="bi bi-reply"></i> Xử lý & Phản hồi
          </button>
        </div>
      </div>
    `;
  }

  card.innerHTML = `
    <div class="feedback-header">
      <div>
        <div class="feedback-title">${escapeHtml(fb.title)}</div>
        <div class="feedback-meta mt-1">
          ${studentDisplay}
          <span><i class="bi bi-calendar3"></i> ${formatDate(fb.created_at)}</span>
          ${sentiHtml}
        </div>
      </div>
      <div>
        ${statusHtml}
      </div>
    </div>

    <div class="feedback-content">
      ${escapeHtml(fb.content)}
      ${fb.attachment_url ? `<div class="mt-2"><small><i class="bi bi-paperclip"></i> Đính kèm: <a href="${fb.attachment_url}" target="_blank" class="text-decoration-underline">${fb.attachment_url}</a></small></div>` : ''}
    </div>

    <div class="d-flex align-items-center flex-wrap gap-2">
      <small class="text-muted fw-bold me-1">Danh mục:</small>
      ${catsHtml}
    </div>

    ${responsesHtml}

    ${adminActionsHtml}
  `;

  return card;
}

// ====================================================================
// 9. Modal Xử lý & Phản hồi cho Sinh viên (Admin Action)
// ====================================================================
function openRespondModal(feedbackId, title) {
  document.getElementById('modal-respond-fb-id').value = feedbackId;
  document.getElementById('modal-respond-title').textContent = title;
  document.getElementById('modal-respond-content').value = '';
  document.getElementById('modal-respond-container').style.display = 'flex';
}

function closeRespondModal() {
  document.getElementById('modal-respond-container').style.display = 'none';
}

document.getElementById('btn-send-response').addEventListener('click', async () => {
  const feedbackId = document.getElementById('modal-respond-fb-id').value;
  const content = document.getElementById('modal-respond-content').value.trim();
  const updateStatus = document.getElementById('modal-respond-status').value;
  const dept = document.getElementById('modal-respond-dept').value;

  if (!content) {
    alert('Vui lòng nhập nội dung phản hồi cho sinh viên.');
    return;
  }

  try {
    // 1. Cập nhật phòng ban và trạng thái
    await fetch(`/api/feedbacks/${feedbackId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: updateStatus, assigned_department: dept })
    });

    // 2. Gửi câu trả lời
    await fetch(`/api/feedbacks/${feedbackId}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        staff_id: AppState.currentUser.id,
        response_content: content,
        update_status_to: updateStatus
      })
    });

    closeRespondModal();
    alert('Đã gửi phản hồi và cập nhật tiến độ thành công!');
    loadAdminFeedbacks();
  } catch (err) {
    console.error('Lỗi khi gửi phản hồi:', err);
    alert('Có lỗi xảy ra khi gửi phản hồi.');
  }
});

// ====================================================================
// 10. Modal Override Nhãn AI (Human-in-the-loop / Active Learning)
// ====================================================================
async function openOverrideModal(feedbackId) {
  try {
    const res = await fetch(`/api/feedbacks/${feedbackId}`);
    const fb = await res.json();

    document.getElementById('modal-override-fb-id').value = feedbackId;
    document.getElementById('modal-override-content').textContent = fb.content;

    const checkboxContainer = document.getElementById('modal-override-checkboxes');
    checkboxContainer.innerHTML = '';

    const currentCatIds = fb.categories.map(c => c.category_id);

    AppState.categories.forEach(cat => {
      const isChecked = currentCatIds.includes(cat.category_id);
      const div = document.createElement('div');
      div.className = 'form-check mb-2';
      div.innerHTML = `
        <input class="form-check-input" type="checkbox" value="${cat.category_id}" id="chk-cat-${cat.category_id}" ${isChecked ? 'checked' : ''}>
        <label class="form-check-label d-flex align-items-center gap-2" for="chk-cat-${cat.category_id}">
          <span class="badge-category" style="background-color: ${cat.color};">
            <i class="bi ${cat.icon}"></i> ${cat.category_name}
          </span>
          <small class="text-muted">${cat.description || ''}</small>
        </label>
      `;
      checkboxContainer.appendChild(div);
    });

    document.getElementById('modal-override-container').style.display = 'flex';
  } catch (err) {
    alert('Không thể tải thông tin phản hồi để sửa nhãn.');
  }
}

function closeOverrideModal() {
  document.getElementById('modal-override-container').style.display = 'none';
}

document.getElementById('btn-save-override').addEventListener('click', async () => {
  const feedbackId = document.getElementById('modal-override-fb-id').value;
  const checkboxes = document.querySelectorAll('#modal-override-checkboxes input:checked');
  const selectedIds = Array.from(checkboxes).map(c => parseInt(c.value));

  if (selectedIds.length === 0) {
    alert('Vui lòng chọn ít nhất 1 danh mục!');
    return;
  }

  try {
    const res = await fetch(`/api/feedbacks/${feedbackId}/override-categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        admin_id: AppState.currentUser.id,
        category_ids: selectedIds
      })
    });

    const result = await res.json();
    closeOverrideModal();
    alert('✅ ' + result.message);
    loadAdminFeedbacks();
  } catch (err) {
    alert('Lỗi lưu nhãn điều chỉnh.');
  }
});

async function quickApproveAI(feedbackId) {
  try {
    const res = await fetch(`/api/feedbacks/${feedbackId}`);
    const fb = await res.json();
    const currentCatIds = fb.categories.map(c => c.category_id);

    await fetch(`/api/feedbacks/${feedbackId}/override-categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        admin_id: AppState.currentUser.id,
        category_ids: currentCatIds
      })
    });

    alert('✅ Đã xác nhận phê duyệt kết quả phân loại của AI!');
    loadAdminFeedbacks();
  } catch (err) {
    alert('Lỗi duyệt AI');
  }
}

// ====================================================================
// 11. Thống Kê & Biểu Đồ Dashboard (Chart.js / Canvas)
// ====================================================================
let categoryChartInstance = null;
let sentimentChartInstance = null;

async function loadDashboardAnalytics() {
  try {
    const res = await fetch('/api/analytics/summary');
    const data = await res.json();

    // Stats counter
    document.getElementById('stat-total-feedbacks').textContent = data.status_counts.total || 0;
    document.getElementById('stat-pending-feedbacks').textContent = data.status_counts.pending || 0;
    document.getElementById('stat-processing-feedbacks').textContent = data.status_counts.processing || 0;
    document.getElementById('stat-resolved-feedbacks').textContent = data.status_counts.resolved || 0;
    document.getElementById('stat-urgent-feedbacks').textContent = data.sentiment_counts.urgent || 0;
    document.getElementById('stat-ai-accuracy').textContent = `${data.ai_accuracy.accuracy_rate}%`;

    // Render Charts
    renderCategoryChart(data.category_distribution);
    renderSentimentChart(data.sentiment_counts);

  } catch (err) {
    console.error('Lỗi tải thống kê dashboard:', err);
  }
}

function renderCategoryChart(catData) {
  const ctx = document.getElementById('chart-category-distribution').getContext('2d');
  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  const labels = catData.map(c => c.category_name);
  const counts = catData.map(c => c.count);
  const colors = catData.map(c => c.color || '#3b82f6');

  categoryChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Số lượng phản hồi',
        data: counts,
        backgroundColor: colors,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.raw} phản hồi`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  });
}

function renderSentimentChart(sentiData) {
  const ctx = document.getElementById('chart-sentiment-distribution').getContext('2d');
  if (sentimentChartInstance) {
    sentimentChartInstance.destroy();
  }

  sentimentChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Tích cực (Positive)', 'Trung tính (Neutral)', 'Tiêu cực (Negative)'],
      datasets: [{
        data: [sentiData.positive || 0, sentiData.neutral || 0, sentiData.negative || 0],
        backgroundColor: ['#10b981', '#94a3b8', '#ef4444'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

// ====================================================================
// 12. Thiết Kế Cơ Sở Dữ Liệu & ERD Viewer
// ====================================================================
async function loadDatabaseSchema() {
  const container = document.getElementById('erd-tables-container');
  try {
    const res = await fetch('/api/db/schema-info');
    const data = await res.json();

    container.innerHTML = '';
    data.tables.forEach(tbl => {
      const tableDiv = document.createElement('div');
      tableDiv.className = 'erd-table';
      
      let rowsHtml = '';
      tbl.columns.forEach(col => {
        const pkBadge = col.pk ? '<span class="badge bg-danger">PK</span>' : '';
        const fkBadge = col.fk ? `<span class="badge bg-info text-dark">FK &rarr; ${col.fk}</span>` : '';
        const constraint = col.constraint ? `<small class="text-muted">(${col.constraint})</small>` : '';

        rowsHtml += `
          <div class="erd-row">
            <div class="erd-col-name"><strong>${col.name}</strong> ${pkBadge} ${fkBadge}</div>
            <div class="erd-col-type">${col.type} ${constraint}</div>
            <div class="erd-col-desc">${col.description}</div>
          </div>
        `;
      });

      tableDiv.innerHTML = `
        <div class="erd-header">
          <span><i class="bi bi-table me-2"></i> Bảng: <code>${tbl.name}</code></span>
          <small class="opacity-75">${tbl.description}</small>
        </div>
        ${rowsHtml}
      `;
      container.appendChild(tableDiv);
    });
  } catch (err) {
    container.innerHTML = '<div class="alert alert-danger">Lỗi tải schema CSDL.</div>';
  }
}

// Copy DDL script helper
function copySqlDdl(dialect) {
  let file = 'schema.sql';
  if (dialect === 'mysql') file = 'schema_mysql.sql';
  if (dialect === 'postgres') file = 'schema_postgres.sql';

  fetch(`/database/${file}`)
    .then(r => r.text())
    .then(text => {
      navigator.clipboard.writeText(text);
      alert(`Đã sao chép kịch bản SQL DDL (${dialect.toUpperCase()}) vào Clipboard!`);
    })
    .catch(() => alert('Không thể tải file SQL.'));
}

// ====================================================================
// 13. AI Retrain Logs (Vòng lặp phản hồi cải thiện mô hình)
// ====================================================================
async function loadRetrainLogs() {
  const container = document.getElementById('retrain-logs-tbody');
  container.innerHTML = '<tr><td colspan="6" class="text-center py-3"><span class="spinner-border spinner-border-sm"></span> Đang tải...</td></tr>';

  try {
    const res = await fetch('/api/ai/retrain-logs');
    const logs = await res.json();

    if (logs.length === 0) {
      container.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Chưa có bản ghi hiệu chỉnh nào. Hãy vào tab BQL để duyệt hoặc sửa nhãn.</td></tr>';
      return;
    }

    container.innerHTML = '';
    logs.forEach(log => {
      const tr = document.createElement('tr');
      const pred = JSON.parse(log.predicted_categories || '[]');
      const appr = JSON.parse(log.approved_categories || '[]');

      tr.innerHTML = `
        <td>#${log.log_id}</td>
        <td><small class="text-dark">${escapeHtml(log.feedback_text)}</small></td>
        <td>${pred.map(p => `<span class="badge bg-secondary me-1">${p}</span>`).join('')}</td>
        <td>${appr.map(a => `<span class="badge bg-primary me-1">${a}</span>`).join('')}</td>
        <td>
          ${log.was_modified 
            ? '<span class="badge bg-warning text-dark"><i class="bi bi-pencil-fill"></i> Có điều chỉnh</span>' 
            : '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Giữ nguyên AI</span>'}
        </td>
        <td><small class="text-muted">${formatDate(log.created_at)}</small></td>
      `;
      container.appendChild(tr);
    });
  } catch (err) {
    container.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Lỗi tải Retrain Logs.</td></tr>';
  }
}

// Helpers
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function formatDate(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });
}
