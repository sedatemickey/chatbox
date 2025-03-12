<template>
    <div class="login-container">
        <div class="login-box">
            <h1 class="title">ChatBox</h1>
            <form @submit.prevent="login">
                <div class="form-group">
                    <input
                        v-model="form.username"
                        type="text"
                        required
                        class="input-field"
                    />
                    <label class="input-label">用户名</label>
                </div>
                
                <div class="form-group">
                    <input
                        v-model="form.password"
                        type="password"
                        required
                        class="input-field"
                    />
                    <label class="input-label">密码</label>
                </div>
        
                <button type="submit" class="login-btn">登 录</button>
            </form>
    
            <router-link to="/register" class="register-link">没有账号？<span>立即注册</span></router-link>
        </div>
    </div>
</template>
  
<script lang="ts">
import { handleLogin, checkToken } from '@/services/api/auth'
export default {
    data() {
        return {
            form: {
                username: '',
                password: ''
            }
        }
    },
    created() {
        if(checkToken() === true) {
            this.$router.push('/chat')
        }
    },
    methods: {
        login() {
            console.log('登录信息:', this.form)
            handleLogin(this.form.username, this.form.password)
        }
    }
}
</script>
  
<style scoped>
.login-container {
    min-height: 100vh;
    background: url('/bg.jpg') no-repeat center center fixed;
    background-size: cover;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-box {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(12px);
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    width: 420px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.title {
    color: #fff;
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2em;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
    position: relative;
    margin-bottom: 2rem;
}

.input-field {
    width: 100%;
    padding: 12px 20px;
    border: none;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #fff;
    font-size: 16px;
    transition: all 0.3s ease;
}

.input-field:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.input-label {
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.6);
    pointer-events: none;
    transition: all 0.3s ease;
}

.input-field:focus ~ .input-label,
.input-field:valid ~ .input-label {
    top: -10px;
    left: 5px;
    font-size: 12px;
    color: #fff;
}

.login-btn {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.register-link {
    display: block;
    text-align: center;
    margin-top: 1.5rem;
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-size: 14px;
}

.register-link span {
    color: #fff;
    font-weight: 500;
    border-bottom: 1px solid transparent;
    transition: all 0.3s ease;
}

.register-link:hover span {
    border-bottom-color: #fff;
}

@media (max-width: 480px) {
    .login-box {
    width: 90%;
    padding: 30px;
    }
}
</style>