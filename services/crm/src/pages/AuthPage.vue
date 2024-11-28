<template>
	<div class="content">
		<modal-window @close="onClose" class="modal-window">
			<div class="label">
				<div class="keys"></div>
				<p>Авторизуйтесь</p>
			</div>
			<form @submit.prevent="onSubmit">
				<div class="inputs">
					<border-input
						v-model:value="login"
						placeholder="Логин"
						auto
						id="username"
						autocomplete="username"
					></border-input>
					<border-input
						v-model:value="password"
						placeholder="Пароль"
						id="password"
						autocomplete="current-password"
						type="password"
					></border-input>
				</div>
				<purple-button :disabled="submitting" :class="{ disabled: submitting }">
					<p style="margin: 0">Войти</p>
				</purple-button>
				<div class="loader-wrapper" v-if="submitting">
					<CircleLoader class="loader"></CircleLoader>
				</div>
			</form>
		</modal-window>
	</div>
</template>
<script setup lang="ts">
import ModalWindow from "@/components/ModalWindow.vue";
import CircleLoader from "@/components/UI/CircleLoader.vue";
import router from "@/router";
import { useNetworkStore } from "@/store/network";
import { ref } from "vue";

const onAuth = async () => {
	await router.replace({ name: "home" });
};

const networkStore = useNetworkStore();

const login = ref("");
const password = ref("");

const submitting = ref(false);

const onSubmit = async () => {
	submitting.value = true;
	if (await networkStore.login(login.value, password.value)) {
		await onAuth();
	} else {
		login.value = "";
		password.value = "";
	}
	submitting.value = false;
};
const onClose = () => {
	window.location.href = "https://fuji.ru";
};
</script>
<style scoped>
.content {
	background-image: url("/img/auth-bg.jpg");
	background-size: cover;
	width: 100%;
	height: 100%;
}

.label {
	width: 460px;
	height: 116px;
	display: flex;
	flex-direction: column;
	align-items: center;
	position: relative;
}

.label .keys {
	width: 90px;
	height: 90px;
	background-image: url("/img/auth-keys.gif");
	background-size: cover;
	position: relative;
	top: -10px;
}

@font-face {
	font-family: benzin-regular;
	src: url("/font/benzin-regular.ttf") format("truetype");
}

.label p {
	font-weight: 600;
	font-size: 24px;
	font-family: benzin-regular;
	margin: 0;
	color: #292929;
}

form {
	width: 100%;
	height: 224px;
	display: flex;
	flex-direction: column;
	gap: 25px;

	.inputs {
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.button {
		&.disabled {
			background-color: gray;
			cursor: not-allowed;
		}
	}

	.loader-wrapper {
		display: flex;
		flex-direction: row;
		justify-content: center;
		position: relative;

		flex: 1;

		width: 100%;

		.loader {
			bottom: 0;
			height: 30px;
			width: 30px;
		}
	}
}
</style>
