import requests
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import gitea_settings

# ===== 配置 =====
GITEA_BASE_URL = gitea_settings.gitea_base_url
API_TOKEN = gitea_settings.gitea_api_token
OWNER = gitea_settings.gitea_owner
REPO = gitea_settings.gitea_repo
AUTHOR_NAME = gitea_settings.gitea_author_name
AUTHOR_EMAIL = gitea_settings.gitea_author_email
BRANCH = gitea_settings.gitea_branch


def fetch_commits(owner, repo, branch="main", per_page=50):
    """获取指定分支的所有提交"""
    commits = []
    url = f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/commits"
    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}

    page = 1
    while True:
        params = {"sha": branch, "limit": per_page, "page": page}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            if "resp" in locals() and resp is not None:
                print("返回内容:", resp.text)
            break

        data = resp.json()
        if not data:
            break

        commits.extend(data)
        page += 1

    return commits


def filter_commits(commits, author_email=None, author_name=None, days=None):
    """
    筛选指定作者的提交，并根据时间范围过滤
    - 优先匹配邮箱，其次匹配名字
    - days: None=不过滤, 0=今天, 7=最近7天, 30=最近30天
    """
    result = []
    now = datetime.now(timezone.utc)

    for c in commits:
        commit_info = c.get("commit", {})
        author_info = commit_info.get("author", {})

        name = author_info.get("name")
        email = author_info.get("email")
        date_str = author_info.get("date")
        try:
            # 处理不同的日期格式
            if date_str.endswith("Z"):
                # UTC时间格式: 2025-01-10T10:05:33Z
                commit_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            elif "+" in date_str or date_str.count("-") > 2:
                # 带时区偏移格式: 2025-09-10T18:05:33+08:00
                commit_date = datetime.fromisoformat(date_str)
            else:
                # 简单格式: 2025-01-10T10:05:33
                commit_date = datetime.fromisoformat(date_str)
        except Exception as e:
            print(f"⚠️ 日期解析失败: {date_str}, 错误: {e}")
            commit_date = None

        # 过滤作者
        if author_email and email == author_email:
            pass
        elif author_name and name == author_name:
            pass
        else:
            continue

        # 过滤时间
        if days is not None and commit_date is not None:
            if days == 0:  # 今天
                if commit_date.date() != now.date():
                    continue
            else:  # 最近 N 天
                if commit_date < now - timedelta(days=days):
                    continue

        result.append(c)

    return result


def fetch_commit_details(owner, repo, sha, debug=False):
    """获取单个commit的详细信息"""
    # 尝试不同的Gitea API路径
    possible_urls = [
        f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/git/commits/{sha}",
        f"{GITEA_BASE_URL}/api/v1/repos/{owner.strip()}/{repo.strip()}/commits/{sha}",
    ]

    headers = {"Authorization": f"token {API_TOKEN}", "Accept": "application/json"}

    for i, url in enumerate(possible_urls, 1):
        try:
            if debug:
                print(f"🔍 尝试API路径 {i}/{len(possible_urls)}: {url}")
            else:
                print(f"🔍 尝试获取详细信息...")

            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                if debug:
                    print(f"✅ 成功获取commit详情 (使用路径 {i})")
                else:
                    print(f"✅ 成功获取commit详情")
                return resp.json()
            else:
                if debug:
                    print(f"❌ 状态码: {resp.status_code}")
                    print(
                        f"   响应内容: {resp.text[:200]}{'...' if len(resp.text) > 200 else ''}"
                    )
        except requests.RequestException as e:
            if debug:
                print(f"❌ 请求失败: {e}")

    if debug:
        print("❌ 所有API路径都失败了")
    else:
        print("❌ 无法获取commit详细信息")
    return None


def print_commit_details(commit_data):
    """打印commit的详细信息"""
    if not commit_data:
        print("❌ 无法获取commit详细信息")
        return

    print("\n" + "=" * 80)
    print("📋 COMMIT 详细信息")
    print("=" * 80)

    # 基本信息 - 适配Gitea的数据结构
    sha = commit_data.get("sha", commit_data.get("id", ""))

    # Gitea可能直接返回commit信息，而不是嵌套在commit字段中
    if "commit" in commit_data:
        commit_info = commit_data.get("commit", {})
        author_info = commit_info.get("author", {})
        committer_info = commit_info.get("committer", {})
    else:
        # 如果数据结构不同，直接从根级别获取
        commit_info = commit_data
        author_info = commit_data.get("author", {})
        committer_info = commit_data.get("committer", {})

    print(f"🔗 SHA: {sha}")

    # 处理多行提交信息
    message = commit_info.get("message", "无")
    if "\n" in message:
        lines = message.split("\n")
        print(f"📝 提交信息: {lines[0]}")
        if len(lines) > 1:
            print("📄 详细描述:")
            for line in lines[1:]:
                if line.strip():
                    print(f"    {line}")
    else:
        print(f"📝 提交信息: {message}")

    author_name = author_info.get("name", "未知")
    author_email = author_info.get("email", "未知")
    author_date = format_date(author_info.get("date", "未知"))

    committer_name = committer_info.get("name", "未知")
    committer_email = committer_info.get("email", "未知")
    committer_date = format_date(committer_info.get("date", "未知"))

    # 如果作者和提交者是同一人，只显示一次
    if author_name == committer_name and author_email == committer_email:
        print(f"👤 作者: {author_name} <{author_email}>")
        print(f"📅 提交时间: {author_date}")
        if author_date != committer_date:
            print(f"📅 提交者时间: {committer_date}")
    else:
        print(f"👤 作者: {author_name} <{author_email}>")
        print(f"📅 提交时间: {author_date}")
        print(f"👤 提交者: {committer_name} <{committer_email}>")
        print(f"📅 提交者时间: {committer_date}")

    # 统计信息
    stats = commit_data.get("stats", {})
    if stats and any(
        stats.get(key, 0) > 0 for key in ["additions", "deletions", "total"]
    ):
        additions = stats.get("additions", 0)
        deletions = stats.get("deletions", 0)
        total = stats.get("total", 0)
        print(f"📊 统计: +{additions} 行, -{deletions} 行, {total} 行变更")

    # 文件变更 - 改进显示逻辑
    files = commit_data.get("files", [])
    if files:
        print(f"\n📁 文件变更 ({len(files)} 个文件):")
        print("-" * 80)

        # 询问是否显示文件结构调试信息
        if len(files) > 0:
            show_debug = (
                input("🔍 是否显示文件数据结构调试信息？(y/N): ").strip().lower()
            )
            if show_debug == "y":
                print("\n🔍 调试信息 - 第一个文件的数据结构:")
                print(json.dumps(files[0], indent=2, ensure_ascii=False))
                print("-" * 40)

        for i, file_info in enumerate(files, 1):

            filename = file_info.get("filename", file_info.get("name", "未知文件"))

            # 处理不同的状态字段 - Gitea可能使用不同的字段名
            status = file_info.get("status", "")

            # 尝试其他可能的状态字段
            if not status:
                status = file_info.get("type", "")
            if not status:
                status = file_info.get("change_type", "")

            # 如果仍然没有状态，根据变更数量推断
            if not status:
                additions = file_info.get("additions", 0)
                deletions = file_info.get("deletions", 0)

                if additions > 0 and deletions > 0:
                    status = "modified"
                elif additions > 0 and deletions == 0:
                    status = "added"
                elif additions == 0 and deletions > 0:
                    status = "deleted"
                elif file_info.get("binary", False):
                    status = "binary"
                else:
                    # 检查是否有其他指示器
                    if "previous_filename" in file_info or "old_name" in file_info:
                        status = "renamed"
                    else:
                        status = "modified"  # 默认为修改

            additions = file_info.get("additions", 0)
            deletions = file_info.get("deletions", 0)
            changes = file_info.get("changes", additions + deletions)

            status_emoji = {
                "added": "➕",
                "modified": "📝",
                "deleted": "❌",
                "renamed": "🔄",
                "binary": "📦",
                "unknown": "❓",
            }.get(
                status, "📝"
            )  # 默认为修改图标

            status_text = {
                "added": "新增",
                "modified": "修改",
                "deleted": "删除",
                "renamed": "重命名",
                "binary": "二进制",
                "unknown": "未知",
            }.get(
                status, "修改"
            )  # 默认为修改

            print(f"{i:2d}. {status_emoji} {filename}")

            # 如果是重命名，显示原文件名
            old_name = file_info.get("previous_filename", file_info.get("old_name", ""))
            if old_name and old_name != filename:
                print(f"     原文件名: {old_name}")

            if changes > 0 or additions > 0 or deletions > 0:
                print(
                    f"     状态: {status_text} | +{additions} -{deletions} ({changes} 行变更)"
                )
            else:
                print(f"     状态: {status_text}")

            # 如果是二进制文件，特别说明
            if file_info.get("binary", False):
                print(f"     📦 二进制文件")

            # 显示文件大小变化（如果有）
            if "size" in file_info:
                print(f"     📏 文件大小: {file_info['size']} 字节")

    # 链接
    html_url = commit_data.get("html_url", "")
    if html_url:
        print(f"\n🔗 查看链接: {html_url}")

    print("=" * 80)


def format_date(date_str):
    """格式化日期显示"""
    if not date_str or date_str == "未知":
        return "未知时间"

    try:
        # 解析ISO格式日期
        if date_str.endswith("Z"):
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(date_str)

        # 转换为本地时间显示
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str


def print_commits(commits, author, owner, repo):
    """打印目标作者的提交（倒序显示，最新的在前面）"""
    if not commits:
        print("📭 没有找到符合条件的提交记录")
        return []

    print(f"\n🎯 用户 {author} 在仓库 {owner}/{repo} 的提交总数: {len(commits)}")
    print("=" * 120)

    # 按提交时间倒序排列（最新的在前面）
    sorted_commits = sorted(
        commits,
        key=lambda c: c.get("commit", {}).get("author", {}).get("date", ""),
        reverse=True,
    )

    # 表头
    print(f"{'序号':<4} {'SHA':<8} {'时间':<20} {'提交信息':<60} {'链接'}")
    print("-" * 120)

    for i, c in enumerate(sorted_commits, 1):
        sha = c.get("sha", "")[:7]
        commit_info = c.get("commit", {})
        message = commit_info.get("message", "").split("\n")[0]
        # 截断过长的提交信息
        if len(message) > 57:
            message = message[:54] + "..."

        author_info = commit_info.get("author", {})
        date = format_date(author_info.get("date", "未知时间"))
        url = c.get("html_url", "无链接")

        # 美化时间显示
        if date != "未知时间":
            date = (
                date.split(" ")[0] + " " + date.split(" ")[1][:8]
            )  # 只显示日期和时分秒

        print(f"{i:2d}.  {sha:<8} {date:<20} {message:<60} {url}")

    print("=" * 120)
    return sorted_commits


def show_commit_details_menu(commits, owner, repo):
    """显示commit详情选择菜单"""
    if not commits:
        print("❌ 没有找到提交记录")
        return

    while True:
        print(f"\n📋 共找到 {len(commits)} 条提交记录")
        print("请选择操作:")
        print("1. 查看某个commit的详细信息")
        print("2. 启用调试模式查看commit")
        print("3. 返回主菜单")

        try:
            detail_choice = input("请输入选项 (1-3): ").strip()

            if detail_choice == "1":
                commit_details = select_and_fetch_commit(
                    commits, owner, repo, debug=False
                )
                if commit_details:
                    print_commit_details(commit_details)
            elif detail_choice == "2":
                commit_details = select_and_fetch_commit(
                    commits, owner, repo, debug=True
                )
                if commit_details:
                    print_commit_details_with_debug(commit_details)
            elif detail_choice == "3":
                break
            else:
                print("❌ 无效选项，请输入 1-3")

        except KeyboardInterrupt:
            print("\n👋 返回主菜单")
            break


def select_and_fetch_commit(commits, owner, repo, debug=False):
    """选择并获取commit详细信息"""
    try:
        commit_num = int(
            input(f"请输入要查看的commit编号 (1-{len(commits)}): ").strip()
        )
        if 1 <= commit_num <= len(commits):
            selected_commit = commits[commit_num - 1]
            sha = selected_commit.get("sha", "")

            print(f"\n⏳ 正在获取commit {sha[:7]} 的详细信息...")
            commit_details = fetch_commit_details(owner, repo, sha, debug=debug)
            return commit_details
        else:
            print(f"❌ 请输入 1-{len(commits)} 之间的数字")
            return None
    except ValueError:
        print("❌ 请输入有效的数字")
        return None


def print_commit_details_with_debug(commit_data):
    """打印commit详细信息（包含调试信息）"""
    if not commit_data:
        print("❌ 无法获取commit详细信息")
        return

    print("\n" + "=" * 80)
    print("🔍 COMMIT 详细信息 (调试模式)")
    print("=" * 80)

    print("\n🔍 原始数据结构:")
    print(json.dumps(commit_data, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("📋 格式化显示:")
    print("=" * 80)

    # 调用正常的显示函数
    print_commit_details(commit_data)


def show_menu():
    """显示菜单选项"""
    print("\n" + "=" * 60)
    print("📊 Gitea 提交记录查询工具")
    print(f"🔗 仓库: {OWNER}/{REPO}")
    print(f"👤 作者: {AUTHOR_NAME} <{AUTHOR_EMAIL}>")
    print("=" * 60)
    print("请选择要查看的时间范围:")
    print("1. 📅 今天的提交")
    print("2. 📅 最近7天的提交")
    print("3. 📅 最近30天的提交")
    print("4. 📅 所有提交")
    print("5. ⚙️  修改配置")
    print("0. 🚪 退出程序")
    print("-" * 60)


def show_config_menu():
    """显示配置菜单"""
    print("\n" + "=" * 50)
    print("⚙️ 配置管理")
    print("=" * 50)
    print("当前配置:")
    print(f"🔗 Gitea地址: {GITEA_BASE_URL}")
    print(f"👤 作者名: {AUTHOR_NAME}")
    print(f"📧 作者邮箱: {AUTHOR_EMAIL}")
    print(f"📂 仓库: {OWNER}/{REPO}")
    print(f"🌿 分支: {BRANCH}")
    print("-" * 50)
    print("1. 修改作者邮箱")
    print("2. 修改仓库信息")
    print("3. 返回主菜单")
    print("-" * 50)


def handle_config_change():
    """处理配置修改"""
    global AUTHOR_EMAIL, OWNER, REPO, BRANCH

    while True:
        show_config_menu()
        try:
            choice = input("请输入选项 (1-3): ").strip()

            if choice == "1":
                new_email = input(
                    f"请输入新的作者邮箱 (当前: {AUTHOR_EMAIL}): "
                ).strip()
                if new_email:
                    AUTHOR_EMAIL = new_email
                    print(f"✅ 作者邮箱已更新为: {AUTHOR_EMAIL}")
            elif choice == "2":
                new_owner = input(f"请输入仓库拥有者 (当前: {OWNER}): ").strip()
                new_repo = input(f"请输入仓库名 (当前: {REPO}): ").strip()
                new_branch = input(f"请输入分支名 (当前: {BRANCH}): ").strip()

                if new_owner:
                    OWNER = new_owner
                if new_repo:
                    REPO = new_repo
                if new_branch:
                    BRANCH = new_branch

                print(f"✅ 仓库信息已更新为: {OWNER}/{REPO} (分支: {BRANCH})")
            elif choice == "3":
                break
            else:
                print("❌ 无效选项，请输入 1-3")

        except KeyboardInterrupt:
            print("\n👋 返回主菜单")
            break


def show_startup_banner():
    """显示启动横幅"""
    print("\n" + "=" * 60)
    print("🚀 Gitea 提交记录查询工具")
    print("=" * 60)
    print("📋 功能特性:")
    print("  • 📅 按时间范围查询提交记录")
    print("  • 🔍 查看详细的commit信息")
    print("  • 📊 显示文件变更和统计数据")
    print("  • ⚙️  动态配置修改")
    print("  • 🐛 调试模式支持")
    print("=" * 60)
    print(f"🔗 当前仓库: {GITEA_BASE_URL}/{OWNER}/{REPO}")
    print(f"👤 查询作者: {AUTHOR_NAME} <{AUTHOR_EMAIL}>")
    print(f"🌿 目标分支: {BRANCH}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        show_startup_banner()
        print("\n⏳ 正在获取提交记录...")
        all_commits = fetch_commits(OWNER, REPO, BRANCH)
        print(f"✅ 成功获取到 {len(all_commits)} 条提交记录")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("请检查网络连接和配置信息")
        exit(1)

    while True:
        show_menu()
        try:
            choice = input("请输入选项 (0-5): ").strip()

            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                commits = filter_commits(
                    all_commits,
                    author_email=AUTHOR_EMAIL,
                    author_name=AUTHOR_NAME,
                    days=0,
                )
                print("\n===== 今天的提交 =====")
                sorted_commits = print_commits(
                    commits, AUTHOR_EMAIL or AUTHOR_NAME, OWNER, REPO
                )
                show_commit_details_menu(sorted_commits, OWNER, REPO)
            elif choice == "2":
                commits = filter_commits(
                    all_commits,
                    author_email=AUTHOR_EMAIL,
                    author_name=AUTHOR_NAME,
                    days=7,
                )
                print("\n===== 最近7天的提交 =====")
                sorted_commits = print_commits(
                    commits, AUTHOR_EMAIL or AUTHOR_NAME, OWNER, REPO
                )
                show_commit_details_menu(sorted_commits, OWNER, REPO)
            elif choice == "3":
                commits = filter_commits(
                    all_commits,
                    author_email=AUTHOR_EMAIL,
                    author_name=AUTHOR_NAME,
                    days=30,
                )
                print("\n===== 最近30天的提交 =====")
                sorted_commits = print_commits(
                    commits, AUTHOR_EMAIL or AUTHOR_NAME, OWNER, REPO
                )
                show_commit_details_menu(sorted_commits, OWNER, REPO)
            elif choice == "4":
                commits = filter_commits(
                    all_commits,
                    author_email=AUTHOR_EMAIL,
                    author_name=AUTHOR_NAME,
                    days=None,
                )
                print("\n===== 所有提交 =====")
                sorted_commits = print_commits(
                    commits, AUTHOR_EMAIL or AUTHOR_NAME, OWNER, REPO
                )
                show_commit_details_menu(sorted_commits, OWNER, REPO)
            elif choice == "5":
                handle_config_change()
                # 配置更改后重新获取提交记录
                print("\n🔄 配置已更改，重新获取提交记录...")
                all_commits = fetch_commits(OWNER, REPO, BRANCH)
                print(f"✅ 成功获取到 {len(all_commits)} 条提交记录")
            else:
                print("❌ 无效选项，请输入 0-5 之间的数字")

        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

        input("\n按回车键继续...")
