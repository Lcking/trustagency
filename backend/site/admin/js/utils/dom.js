/**
 * DOM 操作工具函数
 */

/**
 * 按ID获取元素
 */
export function getById(id) {
    return document.getElementById(id);
}

/**
 * 查询单个元素
 */
export function $(selector, parent = document) {
    return parent.querySelector(selector);
}

/**
 * 查询多个元素
 */
export function $$(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
}

/**
 * 创建元素
 */
export function createElement(tag, attributes = {}, children = []) {
    const element = document.createElement(tag);
    
    // 设置属性
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'classList' && Array.isArray(value)) {
            element.classList.add(...value);
        } else if (key === 'dataset' && typeof value === 'object') {
            Object.assign(element.dataset, value);
        } else if (key === 'style' && typeof value === 'object') {
            Object.assign(element.style, value);
        } else if (key.startsWith('on') && typeof value === 'function') {
            const eventName = key.slice(2).toLowerCase();
            element.addEventListener(eventName, value);
        } else {
            element.setAttribute(key, value);
        }
    });
    
    // 添加子元素
    children.forEach(child => {
        if (typeof child === 'string') {
            element.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
            element.appendChild(child);
        }
    });
    
    return element;
}

/**
 * 显示元素
 */
export function show(element) {
    if (!element) return;
    element.classList.remove('hidden');
    element.style.display = '';
}

/**
 * 隐藏元素
 */
export function hide(element) {
    if (!element) return;
    element.classList.add('hidden');
}

/**
 * 切换显示/隐藏
 */
export function toggle(element) {
    if (!element) return;
    element.classList.toggle('hidden');
}

/**
 * 添加类名
 */
export function addClass(element, ...classNames) {
    if (!element) return;
    element.classList.add(...classNames);
}

/**
 * 移除类名
 */
export function removeClass(element, ...classNames) {
    if (!element) return;
    element.classList.remove(...classNames);
}

/**
 * 切换类名
 */
export function toggleClass(element, className) {
    if (!element) return;
    element.classList.toggle(className);
}

/**
 * 检查是否有类名
 */
export function hasClass(element, className) {
    return element?.classList.contains(className) || false;
}

/**
 * 设置HTML内容
 */
export function setHTML(element, html) {
    if (!element) return;
    element.innerHTML = html;
}

/**
 * 设置文本内容
 */
export function setText(element, text) {
    if (!element) return;
    element.textContent = text;
}

/**
 * 获取表单数据
 */
export function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        // 处理复选框
        if (form.elements[key]?.type === 'checkbox') {
            data[key] = form.elements[key].checked;
        } 
        // 处理数字
        else if (form.elements[key]?.type === 'number') {
            data[key] = value === '' ? null : Number(value);
        }
        // 其他
        else {
            data[key] = value;
        }
    }
    
    return data;
}

/**
 * 设置表单数据
 */
export function setFormData(form, data) {
    Object.entries(data).forEach(([key, value]) => {
        const element = form.elements[key];
        if (!element) return;
        
        if (element.type === 'checkbox') {
            element.checked = !!value;
        } else if (element.type === 'radio') {
            const radio = form.querySelector(`input[name="${key}"][value="${value}"]`);
            if (radio) radio.checked = true;
        } else {
            element.value = value ?? '';
        }
    });
}

/**
 * 清空表单
 */
export function clearForm(form) {
    form.reset();
}

/**
 * 滚动到元素
 */
export function scrollToElement(element, options = {}) {
    if (!element) return;
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
        ...options
    });
}

/**
 * 滚动到顶部
 */
export function scrollToTop(smooth = true) {
    window.scrollTo({
        top: 0,
        behavior: smooth ? 'smooth' : 'auto'
    });
}

/**
 * 委托事件
 */
export function delegate(parent, eventType, selector, handler) {
    parent.addEventListener(eventType, (event) => {
        const target = event.target.closest(selector);
        if (target && parent.contains(target)) {
            handler.call(target, event);
        }
    });
}

/**
 * 移除所有子元素
 */
export function removeChildren(element) {
    if (!element) return;
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

/**
 * 插入HTML (安全)
 */
export function insertHTML(element, position, html) {
    if (!element) return;
    element.insertAdjacentHTML(position, html);
}

/**
 * 批量设置属性
 */
export function setAttributes(element, attributes) {
    if (!element) return;
    Object.entries(attributes).forEach(([key, value]) => {
        element.setAttribute(key, value);
    });
}

/**
 * 批量移除属性
 */
export function removeAttributes(element, ...attributes) {
    if (!element) return;
    attributes.forEach(attr => element.removeAttribute(attr));
}
