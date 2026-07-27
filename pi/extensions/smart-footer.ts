import { isAbsolute, relative, resolve, sep } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";

function sanitizeStatusText(text: string): string {
	return text.replace(/[\r\n\t]/g, " ").replace(/ +/g, " ").trim();
}

function formatTokens(count: number): string {
	if (count < 1000) return count.toString();
	if (count < 10000) return `${(count / 1000).toFixed(1)}k`;
	if (count < 1000000) return `${Math.round(count / 1000)}k`;
	if (count < 10000000) return `${(count / 1000000).toFixed(1)}M`;
	return `${Math.round(count / 1000000)}M`;
}

function formatCwdForFooter(cwd: string, home?: string): string {
	if (!home) return cwd;

	const resolvedCwd = resolve(cwd);
	const resolvedHome = resolve(home);
	const relativeToHome = relative(resolvedHome, resolvedCwd);
	const isInsideHome =
		relativeToHome === "" ||
		(relativeToHome !== ".." && !relativeToHome.startsWith(`..${sep}`) && !isAbsolute(relativeToHome));

	if (!isInsideHome) return cwd;
	return relativeToHome === "" ? "~" : `~${sep}${relativeToHome}`;
}

function keepRight(text: string, width: number, ellipsis = "..."): string {
	if (visibleWidth(text) <= width) return text;
	if (width <= visibleWidth(ellipsis)) return ellipsis.slice(0, Math.max(0, width));

	let suffix = "";
	for (const ch of Array.from(text).reverse()) {
		const candidate = `${ellipsis}${ch}${suffix}`;
		if (visibleWidth(candidate) > width) break;
		suffix = `${ch}${suffix}`;
	}

	return `${ellipsis}${suffix}`;
}

function joinDisplayPath(prefix: string, segments: string[], separator: string): string {
	if (prefix === "/") return `/${segments.join(separator)}`;
	if (prefix) return `${prefix}${separator}${segments.join(separator)}`;
	return segments.join(separator);
}

function smartPathDisplay(displayPath: string, width: number): string {
	if (visibleWidth(displayPath) <= width) return displayPath;

	const separator = displayPath.includes("\\") ? "\\" : "/";
	let prefix = "";
	let rest = displayPath;

	if (rest === "~" || rest === "/") return keepRight(rest, width);
	if (rest.startsWith(`~${separator}`)) {
		prefix = "~";
		rest = rest.slice(2);
	} else if (rest.startsWith(separator)) {
		prefix = separator;
		rest = rest.slice(1);
	} else {
		const windowsPrefix = rest.match(/^[A-Za-z]:[\\/]/)?.[0];
		if (windowsPrefix) {
			prefix = windowsPrefix.slice(0, -1);
			rest = rest.slice(windowsPrefix.length);
		}
	}

	const segments = rest.split(/[\\/]/).filter(Boolean);
	if (segments.length === 0) return keepRight(displayPath, width);

	const full = joinDisplayPath(prefix, segments, separator);
	if (visibleWidth(full) <= width) return full;

	for (let keep = segments.length - 1; keep >= 1; keep--) {
		const tail = segments.slice(-keep).join(separator);
		const candidate = prefix
			? prefix === separator
				? `${separator}...${separator}${tail}`
				: `${prefix}${separator}...${separator}${tail}`
			: `...${separator}${tail}`;
		if (visibleWidth(candidate) <= width) return candidate;
	}

	return keepRight(`...${separator}${segments[segments.length - 1]}`, width);
}

function renderLeftRight(left: string, right: string, width: number): string {
	if (!right) return truncateToWidth(left, width, "...");

	let safeLeft = left;
	if (visibleWidth(safeLeft) > width) {
		safeLeft = truncateToWidth(safeLeft, width, "...");
	}

	const leftWidth = visibleWidth(safeLeft);
	const rightWidth = visibleWidth(right);
	if (leftWidth + 2 + rightWidth <= width) {
		return safeLeft + " ".repeat(width - leftWidth - rightWidth) + right;
	}

	const availableForRight = Math.max(0, width - leftWidth - 2);
	if (availableForRight <= 0) return safeLeft;

	const truncatedRight = truncateToWidth(right, availableForRight, "");
	const truncatedRightWidth = visibleWidth(truncatedRight);
	return safeLeft + " ".repeat(Math.max(1, width - leftWidth - truncatedRightWidth)) + truncatedRight;
}

function getUsageTotals(entries: any[]): {
	input: number;
	output: number;
	cacheRead: number;
	cacheWrite: number;
	cost: number;
} {
	const totals = {
		input: 0,
		output: 0,
		cacheRead: 0,
		cacheWrite: 0,
		cost: 0,
	};

	const addUsage = (usage: any) => {
		if (!usage) return;
		totals.input += usage.input ?? 0;
		totals.output += usage.output ?? 0;
		totals.cacheRead += usage.cacheRead ?? 0;
		totals.cacheWrite += usage.cacheWrite ?? 0;
		totals.cost += usage.cost?.total ?? 0;
	};

	for (const entry of entries) {
		if (entry.type === "message" && entry.message?.usage) {
			addUsage(entry.message.usage);
		} else if ((entry.type === "branch_summary" || entry.type === "compaction") && entry.usage) {
			addUsage(entry.usage);
		}
	}

	return totals;
}

export default function smartFooter(pi: ExtensionAPI) {
	let enabled = true;

	function applyFooter(ctx: any): void {
		if (!enabled) {
			ctx.ui.setFooter(undefined);
			return;
		}

		ctx.ui.setFooter((tui: any, theme: any, footerData: any) => {
			const unsub = footerData.onBranchChange(() => tui.requestRender());

			return {
				dispose: unsub,
				invalidate() {},
				render(width: number): string[] {
					const home = process.env.HOME || process.env.USERPROFILE;
					const branch = footerData.getGitBranch();
					const sessionName = pi.getSessionName();
					const displayCwd = formatCwdForFooter(ctx.cwd, home);
					let pathLineText = smartPathDisplay(displayCwd, width);

					if (sessionName) {
						const withName = `${pathLineText} • ${sessionName}`;
						if (visibleWidth(withName) <= width) {
							pathLineText = withName;
						}
					}

					const totals = getUsageTotals(ctx.sessionManager.getEntries());
					const statsParts: string[] = [];
					if (totals.input) statsParts.push(`↑${formatTokens(totals.input)}`);
					if (totals.output) statsParts.push(`↓${formatTokens(totals.output)}`);
					if (totals.cacheRead) statsParts.push(`R${formatTokens(totals.cacheRead)}`);
					if (totals.cacheWrite) statsParts.push(`W${formatTokens(totals.cacheWrite)}`);
					if (totals.cost) statsParts.push(`$${totals.cost.toFixed(3)}`);

					const leftStats = statsParts.length > 0 ? statsParts.join(" ") : "ready";
					const modelId = ctx.model?.id || "no-model";
					const thinking = ctx.model?.reasoning && ctx.thinkingLevel && ctx.thinkingLevel !== "off"
						? ` • ${ctx.thinkingLevel}`
						: "";
					let rightMeta = `${modelId}${thinking}`;

					if (branch) {
						const withBranch = `${rightMeta} (${branch})`;
						if (visibleWidth(leftStats) + 2 + visibleWidth(withBranch) <= width) {
							rightMeta = withBranch;
						}
					}

					const lines = [
						truncateToWidth(theme.fg("dim", pathLineText), width, theme.fg("dim", "...")),
						renderLeftRight(theme.fg("dim", leftStats), theme.fg("dim", rightMeta), width),
					];

					const extensionStatuses = footerData.getExtensionStatuses();
					if (extensionStatuses.size > 0) {
						const statusLine = Array.from(extensionStatuses.entries())
							.sort(([a], [b]) => a.localeCompare(b))
							.map(([, text]) => sanitizeStatusText(text))
							.join(" ");

						lines.push(truncateToWidth(theme.fg("dim", statusLine), width, theme.fg("dim", "...")));
					}

					return lines;
				},
			};
		});
	}

	pi.on("session_start", async (_event, ctx) => {
		applyFooter(ctx);
	});

	pi.registerCommand("smart-footer", {
		description: "Schaltet den intelligenten Footer ein oder aus",
		handler: async (args, ctx) => {
			const action = args.trim().toLowerCase();

			if (action === "on" || action === "ein") {
				enabled = true;
			} else if (action === "off" || action === "aus") {
				enabled = false;
			} else {
				enabled = !enabled;
			}

			applyFooter(ctx);
			ctx.ui.notify(enabled ? "Intelligenter Footer aktiv" : "Standard-Footer aktiv", "info");
		},
	});
}
