/**
 * 数据验证工具函数
 */

/**
 * 验证邮箱
 */
export function isEmail(value) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(value);
}

/**
 * 验证URL
 */
export function isURL(value) {
    try {
        new URL(value);
        return true;
    } catch {
        return false;
    }
}

/**
 * 验证手机号
 */
export function isPhone(value) {
    const regex = /^1[3-9]\d{9}$/;
    return regex.test(value);
}

/**
 * 验证身份证号
 */
export function isIDCard(value) {
    const regex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
    return regex.test(value);
}

/**
 * 验证非空
 */
export function isRequired(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') return value.trim().length > 0;
    if (Array.isArray(value)) return value.length > 0;
    return true;
}

/**
 * 验证最小长度
 */
export function minLength(value, min) {
    if (!value) return false;
    return String(value).length >= min;
}

/**
 * 验证最大长度
 */
export function maxLength(value, max) {
    if (!value) return true;
    return String(value).length <= max;
}

/**
 * 验证数字范围
 */
export function inRange(value, min, max) {
    const num = Number(value);
    if (isNaN(num)) return false;
    return num >= min && num <= max;
}

/**
 * 验证是否为数字
 */
export function isNumber(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
}

/**
 * 验证是否为整数
 */
export function isInteger(value) {
    return Number.isInteger(Number(value));
}

/**
 * 验证是否为正数
 */
export function isPositive(value) {
    return isNumber(value) && Number(value) > 0;
}

/**
 * 验证密码强度
 * @returns {Object} { valid: boolean, strength: 'weak'|'medium'|'strong', message: string }
 */
export function validatePassword(password) {
    if (!password) {
        return { valid: false, strength: 'weak', message: '密码不能为空' };
    }
    
    if (password.length < 6) {
        return { valid: false, strength: 'weak', message: '密码至少6位' };
    }
    
    let strength = 0;
    
    // 包含小写字母
    if (/[a-z]/.test(password)) strength++;
    // 包含大写字母
    if (/[A-Z]/.test(password)) strength++;
    // 包含数字
    if (/\d/.test(password)) strength++;
    // 包含特殊字符
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    // 长度大于8
    if (password.length >= 8) strength++;
    
    if (strength <= 2) {
        return { valid: true, strength: 'weak', message: '密码强度：弱' };
    } else if (strength <= 3) {
        return { valid: true, strength: 'medium', message: '密码强度：中' };
    } else {
        return { valid: true, strength: 'strong', message: '密码强度：强' };
    }
}

/**
 * 验证表单
 */
export function validateForm(formData, rules) {
    const errors = {};
    
    Object.entries(rules).forEach(([field, fieldRules]) => {
        const value = formData[field];
        
        for (const rule of fieldRules) {
            const { validator, message } = rule;
            
            if (typeof validator === 'function') {
                if (!validator(value, formData)) {
                    errors[field] = message;
                    break;
                }
            }
        }
    });
    
    return {
        valid: Object.keys(errors).length === 0,
        errors
    };
}

/**
 * 常用验证规则
 */
export const validators = {
    required: (message = '此项必填') => ({
        validator: isRequired,
        message
    }),
    
    email: (message = '请输入有效的邮箱') => ({
        validator: isEmail,
        message
    }),
    
    url: (message = '请输入有效的URL') => ({
        validator: isURL,
        message
    }),
    
    phone: (message = '请输入有效的手机号') => ({
        validator: isPhone,
        message
    }),
    
    min: (min, message = `最小长度为${min}`) => ({
        validator: (value) => minLength(value, min),
        message
    }),
    
    max: (max, message = `最大长度为${max}`) => ({
        validator: (value) => maxLength(value, max),
        message
    }),
    
    range: (min, max, message = `请输入${min}-${max}之间的值`) => ({
        validator: (value) => inRange(value, min, max),
        message
    }),
    
    number: (message = '请输入数字') => ({
        validator: isNumber,
        message
    }),
    
    integer: (message = '请输入整数') => ({
        validator: isInteger,
        message
    }),
    
    positive: (message = '请输入正数') => ({
        validator: isPositive,
        message
    }),
    
    custom: (validator, message) => ({
        validator,
        message
    })
};
