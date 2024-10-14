<template>
	<div class="message-window">
		<div class="header">
			<p class="title">{{ props.title }}</p>
			<div class="tools">
				<ClickableIcon
					class="icon"
					img-src="/img/copy.svg"
					@click="onCopy"
				></ClickableIcon>
				<window-cross class="cross" @click="emit('close')"></window-cross>
			</div>
		</div>
		<div class="content">
			<div class="description">
				<p>{{ props.description }}</p>
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import ClickableIcon from "@/components/UI/ClickableIcon.vue";

const emit = defineEmits(["close"]);
const props = defineProps({
	title: {
		type: String,
		required: true,
	},
	description: {
		type: String,
		required: true,
	},
});

const onCopy = () => {
	navigator.clipboard.writeText(props.description);
	alert("Ошибка скопирована!");
};
</script>
<style scoped>
.message-window {
	width: 400px;
	max-height: 200px;
	position: absolute;
	right: 0;
	bottom: 0;
	min-height: 100px;

	background-color: white;
	border-top-left-radius: 20px;
	padding: 15px;
	z-index: 2;
	border: 1px solid #e6e6e6;
}

.header {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;

	width: 100%;
}

.tools {
	display: flex;
	flex-direction: row;
	gap: 5px;
}

.title {
	margin: 0;
	color: #993ca6;
}

.icon {
	width: 20px;
}

.cross {
	height: 20px;
	position: relative;
}

.content {
	display: flex;
	flex-direction: column;

	padding: 5px 0;

	width: 100%;
	height: 150px;
}

.description {
	overflow-y: auto;

	padding-right: 15px;
	word-wrap: break-word;
}

.content p {
	line-break: auto;
}
</style>
